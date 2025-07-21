from sqlite3 import connect, Connection, Cursor
from copy import deepcopy as copy
from urllib.parse import quote
import urllib.request
import subprocess
import platform
import re
import os

import spotipy
import requests
import pandas as pd
from platformdirs import user_cache_dir

from musicdl import Track, Playlist, Album, Artist, TrackContainer
from musicdl.config import config

def retrieve_db_audio(cursor: Cursor, track_id: str) -> tuple[str, str] | tuple[None, None]:
    cursor.execute("SELECT video_id, audio_path FROM audio_files WHERE track_id = ?", (track_id,))
    result = cursor.fetchone()
    if result:
        return result  # (video_id, audio_path)
    return None, None

class SpotifyInterface:
    """
    ```
    spi = SpotifyInterface()
    url = "https://open.spotify.com/track/7qxURPGc7EXM1G8I1MYuDU?si=eda184d2ee414187"
    track_id = re.search("track/([a-zA-Z0-9]+)", url).group(1)
    track = spi.construct_track(track_id)
    ```
    """
    def __init__(self, cursor: Cursor):
        self.cursor = cursor
        self._sp = spotipy.Spotify(
            auth_manager=spotipy.oauth2.SpotifyClientCredentials(
                client_id=config["client_id"],
                client_secret=config["client_secret"]
                )
            )


    def parse_url(self, url) -> tuple[str, str]:
        """
        reads in a spotify url and returns the id and the url_type (track, album, playlist, or artist)
        ```
        f"https://open.spotify.com/track/{id}?si="    -> (id, "track")
        f"https://open.spotify.com/album/{id}?si="    -> (id, "album")
        f"https://open.spotify.com/playlist/{id}?si=" -> (id, "playlist")
        f"https://open.spotify.com/artist/{id}?si="   -> (id, "artist")
        ```
        """

        for url_type in ["track", "album", "playlist", "artist"]:
            if url_type in url:
                match = re.search(f"{url_type}/([a-zA-Z0-9]+)", url)
                if match:
                    return match.group(1), url_type
                else:
                    raise ValueError(f"Invalid URL: {url}")
        raise ValueError(f"Invalid URL: {url}")

    def retrieve_track_container(self, url) -> TrackContainer:
        tc_id, tc_type = self.parse_url(url)
        if tc_type == "track":
            return self.retrieve_track(tc_id)
        elif tc_type == "album":
            return self.retrieve_album(tc_id)
        elif tc_type == "playlist":
            return self.retrieve_playlist(tc_id)
        elif tc_type == "artist":
            return self.retrieve_artist(tc_id)


    def retrieve_track(self, track_id: str) -> Track:
        """
        retrieve individual track
        """
        try:
            sp_track = self._sp.track(track_id)
        except requests.exceptions.ConnectionError as e:
            #print(str(e))
            print("[Errno -3] Temporary failure in name resolution")
            print("Check to see if you have a reliable internet connection")
            exit(1)
        return Track.from_spotify(track_id, sp_track)

    def retrieve_album(self, album_id: str) -> Album:
        """
        retrieve all tracks in an album
        """
        try:
            sp_album = self._sp.album(album_id)
        except requests.exceptions.ConnectionError as e:
            #print(str(e))
            print("[Errno -3] Temporary failure in name resolution")
            print("Check to see if you have a reliable internet connection")
            exit(1)
        return Album.from_spotify(album_id, sp_album=sp_album)

    def retrieve_artist(self, artist_id: str) -> Artist:
        """
        retrieve all albums by an artist (=> all tracks)
        
        singles are considered albums
        """
        try:
            sp_artist = self._sp.artist(artist_id)
        except requests.exceptions.ConnectionError as e:
            #print(str(e))
            print("[Errno -3] Temporary failure in name resolution")
            print("Check to see if you have a reliable internet connection")
            exit(1)
        artist = Artist(sp_artist["name"], sp_artist["id"])

        offset = 0
        while True:
            sp_artist_albums = self._sp.artist_albums(artist_id, include_groups='album,single', limit=50, offset=offset)
            for sp_album in sp_artist_albums['items']:
                album_id = sp_album['id']
                album = self.retrieve_album(album_id)
                artist.albums[album_id] = album
            if len(sp_artist_albums['items']) == 50:
                offset += 50
            else:
                break
        return artist

    def retrieve_playlist(self, playlist_id) -> Playlist:
        """
        retrieve all tracks in a playlist
        """
        try:
            sp_playlist_tracks = self._sp.playlist_tracks(playlist_id)
        except requests.exceptions.ConnectionError as e:
            #print(str(e))
            print("[Errno -3] Temporary failure in name resolution")
            print("Check to see if you have a reliable internet connection")
            exit(1)
        return Playlist.from_spotify(playlist_id, sp_playlist_tracks)

class YoutubeSearchError(requests.exceptions.ConnectionError):
    """Exception raised when a YouTube search fails to return a valid video ID."""
    def __init__(self, message="Invalid YouTube search result. No video ID found.", search_query=None, track=None):
        self.message = message
        message = message + '\nvideo ID of the form "videoId":"MI_XU1iKRRc" not found in youtube request response'
        self.search_query = search_query
        self.track = track
        super().__init__(self.message)

    def __str__(self):
        if self.search_query:
            return f"{self.message}\nSearch query:\n{self.search_query}\nTrack:\n{str(self.track)}"
        return self.message

class YoutubeInterface:
    """
    ```
    track = Track(...)

    yti = YouTubeInterface()
    yti.add_audio(track)

    # youtube video id
    track.video_id
    # path to downloaded mp3
    track.audio_path
    ```
    """
    def __init__(self, cursor: Cursor):
        """
        ensures that yt-dlp is installed to user cache directory

        yt-dlp can be uninstalled with YoutubeInterface.uninstall_ytdlp()
        """
        self.cursor = cursor
        system = platform.system()
        if system == "Darwin":
            binary = "yt-dlp_macos"
        elif system == "Linux":
            binary = "yt-dlp"
        elif system == "Windows":
            binary = "yt-dlp.exe"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

        self.cache_dir = user_cache_dir("musicdl")
        os.makedirs(self.cache_dir, exist_ok=True)
        binary_path = os.path.join(self.cache_dir, binary)
        if not os.path.exists(binary_path):
            print(f"Downloading {binary} to {binary_path}...")
            try:
                urllib.request.urlretrieve(
                    f"https://github.com/yt-dlp/yt-dlp/releases/latest/download/{binary}",
                    binary_path
                )
            except urllib.error.URLError as e:
                #print(str(e))
                print("[Errno -3] Temporary failure in name resolution")
                print("Check to see if you have a reliable internet connection")
                exit(1)
            print("✅ download successful")
            os.chmod(binary_path, 0o755)
        self.yt_dlp = os.path.abspath(binary_path)

    @staticmethod
    def uninstall_ytdlp():
        system = platform.system()
        if system == "Darwin":
            binary = "yt-dlp_macos"
        elif system == "Linux":
            binary = "yt-dlp"
        elif system == "Windows":
            binary = "yt-dlp.exe"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
        cache_dir = os.path.abspath(user_cache_dir("musicdl"))
        binary_path = os.path.abspath(os.path.join(cache_dir, binary))
        if os.path.exists(binary_path):
            os.remove(binary_path)
            os.rmdir(cache_dir)
            print(f"rm {binary_path}")
            print(f"rmdir {cache_dir}")
        else:
            print(f"Already uninstalled {cache_dir}")

    def add_audio(self, tc: TrackContainer, force_replace_existing_download=False) -> TrackContainer|None:
        """
        adds audio mp3(s) to a TrackContainer
        """
        assert isinstance(tc, TrackContainer)
        if isinstance(tc, Track):
            video_id, audio_path = retrieve_db_audio(tc.id)
            if video_id is None:
                return self._add_audio_to_track(tc, force_replace_existing_download)
            else:
                tc.video_id = video_id
                tc.audio_path = audio_path
                return tc
        tc = copy(tc)
        if isinstance(tc, Album) or isinstance(tc, Playlist):
            for track_id, track in tc.tracks.items():
                tc.tracks[track_id] = self._add_audio_to_track(track, force_replace_existing_download)
        elif isinstance(tc, Artist):
            for album_id, album in tc.albums.items():
                tc.albums[album_id] = self.add_audio(album, force_replace_existing_download)
        return tc

    def _add_audio_to_track(self, track: Track, force=False) -> Track:
        """
        adds audio mp3 to track (video_id and audio_path)
        """
        track = copy(track)
        video_id, audio_path = retrieve_db_audio(self.cursor, track.id)
        if video_id is None or force:
            video_id = self._search(track)
            audio_path = self._download(track, video_id, force=force)
            print(f"Audio added to {track.name}")
        else:
            print(f"Audio for {track.name} already exists in database")
        track.video_id = video_id
        track.audio_path = audio_path
        return track


    def _search(self, track: Track) -> str:
        """
        obtain youtube video id by searching youtube.com and retrieving the first search result

        returns the video id
        """
        search_query = f"{track.name} by {track.artist_name} official audio".replace("+", "%2B").replace(" ", "+").replace('"', "%22")
        search_query = quote(search_query, safe="+")

        search_url = "https://www.youtube.com/results?search_query=" + search_query

        request = requests.get(search_url)
        if request.status_code != 200:
            print(request.status_code)
            print(request.headers)
            print(request.reason)
            raise YoutubeSearchError(search_query=search_url)
        html_content = request.text

        match = re.search(r'"videoId":"(.*?)"', html_content)
        if match:
            video_id = match.group(1)
            return video_id
        else:
            #print("todo: implement YouTube Data API call as alternative (rate limited to 100 searches / day)")
            #print(track.name, track.artist)
            raise YoutubeSearchError(search_query=search_url, track=track)

    def _hash_id(self, video_id: str) -> str:
        """
        generate hash for splitting downloaded mp3 into seperate folders,
        based on the youtube video id
        
        this is done for file system access reasons; individual folders 
        with many files are difficult for most file managers to work with
        """
        number_of_folders = 10
        hash_value = sum(ord(char) for char in video_id) % number_of_folders + 1
        if number_of_folders <= 10:
            return f"{hash_value:02}"
        else:
            return f"{hash_value:03}"

    #def add_missing_video_ids(self, tracks: list[Track], max_calls: int|None = 5) -> list[dict]:
        #if max_calls is None:
            #max_calls = len(tracks)
        #num_calls = 0
        #new_tracks = []
        #for track in tracks:
            #if track.video_id is None and (num_calls < max_calls):
                #num_calls += 1
                #try:
                    #video_id = self.search_yt_for_video_id(track)
                    ##video_id = "sq8GBPUb3rk"
                #except requests.exceptions.ConnectionError:
                    #video_id = None
                #track.video_id = video_id
            #new_tracks.append(track)
        #return new_tracks

    def _download(self, track: Track, video_id: str, force=False) -> str:
        """
        use yt-dlp to download the youtube audio stream and save to mp3

        returns the path to the audio file
        """
        artist_name = track.artist_name
        track_name = track.name
        url = f"https://www.youtube.com/watch?v={video_id}"

        if config["hash_audio_path"]:
            output_dir = os.path.join(config["audio_storage"], self._hash_id(video_id))
        else:
            output_dir = config["audio_storage"]
        os.makedirs(output_dir, exist_ok=True)

        audio_path = os.path.join(output_dir, f"{''.join(c for c in artist_name if c.isalnum())}_{''.join(c for c in track_name if c.isalnum())}{video_id}.mp3")
        if os.path.exists(audio_path):
            if force:
                os.remove(audio_path)
            else:
                return audio_path

        yt = [self.yt_dlp, '--extract-audio', '--audio-format', 'mp3', '--quiet', '--no-warnings', '--progress', '--output', audio_path, url]
        output = subprocess.run(yt, capture_output=False, text=True)
        return audio_path

class MusicDB:
    def __init__(self, music_db=None):
        if music_db is None:
            self.music_db = config["music_db"]
        else:
            self.music_db = music_db
        self.conn=None
        self.cursor=None
        self.connect_to_database()
     

    def _insert_track(self, track: Track):
        self.cursor.execute('''
        INSERT OR IGNORE INTO tracks (id, name, album_id, artist_id)
        VALUES (?, ?, ?, ?)
        ''', (track.id, track.name, track.album_id, track.artist_id))

        self.cursor.execute('''
        INSERT OR IGNORE INTO artists (id, name)
        VALUES (?, ?)
        ''', (track.artist_id, track.artist_name))

        self.cursor.execute('''
        INSERT OR IGNORE INTO albums (id, name, artist_id, release_date, image_url)
        VALUES (?, ?, ?, ?, ?)
        ''', (track.album_id, track.album_name, track.artist_id, track.release_date, track.image_url))

        self.cursor.execute('''
        INSERT INTO audio_files (track_id, video_id, audio_path)
        VALUES (?, ?, ?)
        ON CONFLICT(track_id) DO UPDATE SET
        track_id = excluded.track_id,
        video_id = excluded.video_id,
        audio_path = excluded.audio_path;
        ''', (track.id, track.video_id, track.audio_path))
        self.conn.commit()

    def _insert_collection(self, c: Album|Playlist):
        for track in c.tracks.values():
            print(track)
            self._insert_track(track)

    def add(self, tc: TrackContainer):
        assert isinstance(tc, TrackContainer)
        if isinstance(tc, Track):
            self._insert_track(tc)
        elif isinstance(tc, Album) or isinstance(tc, Playlist):
            self._insert_collection(tc)
        elif isinstance(tc, Artist):
            for album in tc.albums.values():
                self._insert_collection(album)

    def connect_to_database(self, musicdb=None) -> tuple[Connection, Cursor]:
        if musicdb is not None:
            self.music_db = musicdb
        basedir = os.path.dirname(os.path.abspath(self.music_db))
        os.makedirs(basedir, exist_ok=True)
        self.conn = connect(self.music_db)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        sql_script = """
        CREATE TABLE IF NOT EXISTS artists (
            id TEXT PRIMARY KEY,
            name TEXT
        );

        CREATE TABLE IF NOT EXISTS albums (
            id TEXT PRIMARY KEY,
            name TEXT,
            artist_id TEXT,
            release_date TEXT,
            image_url TEXT,
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        );

        CREATE TABLE IF NOT EXISTS tracks (
            id TEXT PRIMARY KEY,
            name TEXT,
            album_id TEXT,
            artist_id TEXT,
            FOREIGN KEY (album_id) REFERENCES albums(id),
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        );

        CREATE TABLE IF NOT EXISTS audio_files (
            track_id TEXT PRIMARY KEY,
            video_id TEXT,
            audio_path TEXT,
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        );
        """
        self.cursor.executescript(sql_script)
    
    def reset_database(self):
        if os.path.exists(self.music_db):
            os.remove(self.music_db)
        self.connect_to_database()

    def close(self):
        self.conn.close()

    def to_csv(self, output_directory="./data", single_file=True) -> str|list[str]:
        for file in os.listdir(output_directory):
            if file.endswith(".csv"):
                os.remove(os.path.join(output_directory, file))
        if single_file:
            query = """
            SELECT
                t.id AS track_id,
                t.name AS track_name,
                t.artist_id AS artist_id,
                ar.name AS artist_name,
                t.album_id AS album_id,
                al.name AS album_name,
                al.release_date AS release_date,
                al.image_url AS image_url,
                af.video_id AS video_id,
                af.audio_path AS audio_path
            FROM tracks t
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums al ON t.album_id = al.id
            LEFT JOIN audio_files af ON t.id = af.track_id;
            """

            df = pd.read_sql_query(query, self.conn)
            df["audio_path"] = df["audio_path"].apply(os.path.abspath)
            output_csv = os.path.join(output_directory, "tracks.csv")
            df.to_csv(output_csv, index=False)
            return output_csv


        else:
            queries = {t: f"SELECT * from {t}" for t in ["tracks", "artists", "albums", "audio_files"]}
            output_csvs = []
            for t, q in queries.items():
                output_csv = os.path.join(output_directory, f"{t}_table.csv")
                pd.read_sql_query(q, self.conn).to_csv(output_csv, index=False)
                output_csvs.append(output_csv)
            return output_csvs