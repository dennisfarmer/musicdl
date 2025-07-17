import spotipy
import subprocess
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from urllib.parse import quote
import re
from .env import *
from .db import connect_to_database, write_track_to_db
from . import Track, Playlist, Album, Artist

class YoutubeSearchError(requests.exceptions.ConnectionError):
    """Exception raised when a YouTube search fails to return a valid video ID."""
    def __init__(self, message="Invalid YouTube search result. No video ID found.", search_query=None):
        self.message = message
        self.search_query = search_query
        super().__init__(self.message)

    def __str__(self):
        if self.search_query:
            return f"{self.message} Search query: {self.search_query}"
        return self.message

class SpotifyInterface:
    def __init__(self):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
                )
            )
        #self.conn, self.cursor = connect_to_database()

    #def __del__(self):
        #self.cursor.close()

    #def close(self):
        #self.cursor.close()

    #def open(self):
        #self.conn, self.cursor = connect_to_database()

    def construct_track(self, track_id: str) -> Track:
        """
        retrieve individual track
        """
        sp_track = self.sp.track(track_id)
        return Track.from_spotify(track_id, sp_track)

    def construct_album(self, album_id: str) -> Album:
        """
        retrieve all tracks in an album
        """
        sp_album = self.sp.album(album_id)
        return Album(sp_album_details=sp_album)

    def construct_artist(self, artist_id: str) -> Artist:
        """
        retrieve all tracks by an artist
        """
        sp_artist = self.sp.artist(artist_id)
        artist = Artist(sp_artist["name"], sp_artist["id"])

        offset = 0
        while True:
            sp_artist_albums = self.sp.artist_albums(artist_id, include_groups='album,single', limit=50, offset=offset)
            for sp_album in sp_artist_albums['items']:
                album_id = sp_album['id']
                album = self.construct_album(album_id)
                artist.albums[album_id] = album
            if len(sp_artist_albums['items']) == 50:
                offset += 50
            else:
                break
        return artist

    def construct_playlist(self, playlist_id) -> Playlist:
        """
        retrieve all tracks in a playlist
        """
        sp_playlist_tracks = self.sp.playlist_tracks(playlist_id)
        return Playlist(playlist_id, sp_playlist_tracks)

    def search_track(self, track_name, track_artist):
        self.sp.search


def hash_yt_video_id(video_id: str) -> str:
    hash_value = sum(ord(char) for char in video_id) % 100 + 1
    return f"{hash_value:03}"
    
def search_yt_for_video_id(track: Track, search_blacklist: list = None) -> str:
    search_query = f"{track.name} by {track.artist_name} official audio".replace("+", "%2B").replace(" ", "+").replace('"', "%22")
    search_query = quote(search_query, safe="+")

    search_url = "https://www.youtube.com/results?search_query=" + search_query

    if search_blacklist is not None and search_url in search_blacklist:
        print(f"Audio skipped: blacklist contains {search_url}")
        raise YoutubeSearchError(search_query=search_url)

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
        #print("todo: implement YouTube Data API call as alternative (rate limited)")
        #print(track.name, track.artist)
        raise YoutubeSearchError(search_query=search_url)
        #raise Exception('video ID of the form "videoId":"MI_XU1iKRRc" not found in youtube request response')


#def add_missing_video_ids(tracks: list[Track], max_calls: int|None = 5) -> list[dict]:
    #if max_calls is None:
        #max_calls = len(tracks)
    #num_calls = 0
    #new_tracks = []
    #for track in tracks:
        #if track.video_id is None and (num_calls < max_calls):
            #num_calls += 1
            #try:
                #video_id = search_yt_for_video_id(track)
                ##video_id = "sq8GBPUb3rk"
            #except requests.exceptions.ConnectionError:
                #video_id = None
            #track.video_id = video_id
        #new_tracks.append(track)
    #return new_tracks

def download_audio(artist_name: str, track_name: str, video_id: str, force=False) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    #if os.path.exists(audio_storage) and not use_tmp:
    output_dir = os.path.join(audio_storage, hash_yt_video_id(video_id))
    os.makedirs(output_dir, exist_ok=True)

    audio_path = os.path.join(output_dir, f"{''.join(c for c in artist_name if c.isalnum())}_{''.join(c for c in track_name if c.isalnum())}{video_id}.mp3")
    if os.path.exists(audio_path):
        if force:
            os.remove(audio_path)
        else:
            return audio_path

    print(url)
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