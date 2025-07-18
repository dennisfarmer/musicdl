import spotipy
import subprocess
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from urllib.parse import quote
import re
from .env import *
from copy import deepcopy as copy
#from .db import connect_to_database, write_track_to_db
from . import Track, Playlist, Album, Artist, TrackContainer


class SpotifyInterface:
    """
    ```
    spi = SpotifyInterface()
    track_url = "https://open.spotify.com/track/7qxURPGc7EXM1G8I1MYuDU?si=eda184d2ee414187"
    track_id = track_url.split("/track/")[1].split("?")[0]
    track = spi.construct_track(track_id)
    ```
    """
    def __init__(self):
        self._sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
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

    def retrieve_track_container(self, url) -> Track|Album|Playlist|Artist:
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
        sp_track = self._sp.track(track_id)
        return Track.from_spotify(track_id, sp_track)

    def retrieve_album(self, album_id: str) -> Album:
        """
        retrieve all tracks in an album
        """
        sp_album = self._sp.album(album_id)
        return Album.from_spotify(album_id, sp_album=sp_album)

    def retrieve_artist(self, artist_id: str) -> Artist:
        """
        retrieve all albums by an artist (=> all tracks)
        
        singles are considered albums
        """
        sp_artist = self._sp.artist(artist_id)
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
        sp_playlist_tracks = self._sp.playlist_tracks(playlist_id)
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
    def __init__(self):
        pass

    def add_audio(self, tc: TrackContainer, inplace=True, force_replace_existing_download=False) -> None|Track:
        """
        adds audio mp3(s) to a TrackContainer
        """
        assert isinstance(tc, TrackContainer)
        if isinstance(tc, Track):
            return self._add_audio_to_track(tc, inplace, force_replace_existing_download)
        if not inplace:
            tc = copy(tc)
        if isinstance(tc, Album) or isinstance(tc, Playlist):
            for track_id, track in tc.tracks.items():
                tc.tracks[track_id] = self._add_audio_to_track(track, False, force_replace_existing_download)
        elif isinstance(tc, Artist):
            for album_id, album in tc.albums.items():
                tc.albums[album_id] = self.add_audio(album, False, force_replace_existing_download)
        if not inplace:
            return tc

    def _add_audio_to_track(self, track: Track, inplace=True, force=False) -> None|Track:
        """
        adds audio mp3 to track (video_id and audio_path)
        """
        if not inplace:
            track = copy(track)
        video_id = self._search(track)
        audio_path = self._download(track, video_id, force=force)
        track.video_id = video_id
        track.audio_path = audio_path
        if not inplace:
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

    def _download(self, track: Track, video_id: str, force=False, no_hash=False) -> str:
        """
        use yt-dlp to download the youtube audio stream and save to mp3

        returns the path to the audio file
        """
        artist_name = track.artist_name
        track_name = track.name
        url = f"https://www.youtube.com/watch?v={video_id}"
        if no_hash:
            output_dir = audio_storage
        else:
            output_dir = os.path.join(audio_storage, self._hash_id(video_id))
        os.makedirs(output_dir, exist_ok=True)

        audio_path = os.path.join(output_dir, f"{''.join(c for c in artist_name if c.isalnum())}_{''.join(c for c in track_name if c.isalnum())}{video_id}.mp3")
        if os.path.exists(audio_path):
            if force:
                os.remove(audio_path)
            else:
                return audio_path

        yt = [yt_dlp, '--extract-audio', '--audio-format', 'mp3', '--quiet', '--no-warnings', '--progress', '--output', audio_path, url]
        output = subprocess.run(yt, capture_output=False, text=True)
        return audio_path




















def add_track(track):
    print(track)
def add_playlist():
    pass
def add_album():
    pass
def add_artist():
    pass
def add_custom_track():
    pass