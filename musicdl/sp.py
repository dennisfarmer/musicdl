
from sqlite3 import Cursor
import re

import requests
import spotipy


from .containers import Track, Playlist, Album, Artist, TrackContainer
from .config import config


class SpotifyInterface:
    """
    This is used to create a database of tracks to export as a zip file

    Retrieves track name/artist/albumart from Spotify and creates
    "Track Containers" which represent tracks in a format that
    YoutubeInterfaceCLI can use to lookup the respective youtube_url
    and download the audio
    ```
    spi = SpotifyInterface()
    url = "https://open.spotify.com/track/7qxURPGc7EXM1G8I1MYuDU?si=eda184d2ee414187"
    track_id = re.search("track/([a-zA-Z0-9]+)", url).group(1)
    track = spi.construct_track(track_id)
    ```
    """
    #def __init__(self, cursor: Cursor):
    def __init__(self):
        client_id=config["client_id"],
        client_secret=config["client_secret"]
        if client_id is None or client_secret is None or client_id == "" or client_secret == "":
            print("\n".join([f"Spotify API Credentials not found in environment variables",
                            "Please provide SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:",
                            "##############################################"
                            "# contents of ./.musicdl_env",
                            'SPOTIFY_CLIENT_ID="your client id here"',
                            'SPOTIFY_CLIENT_SECRET="your client secret here"',
                            "##############################################"
                            "https://developer.spotify.com/documentation/web-api/tutorials/getting-started"
                            ]))
            exit(1)
        #self.cursor = cursor
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