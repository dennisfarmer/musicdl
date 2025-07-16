import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from .env import *
from .db import connect_to_database, write_track_to_db
from . import Track, Playlist, Album, Artist


class SpotifyAPI:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                                        client_secret=client_secret))
        self.conn, self.cursor = connect_to_database()
        self.commit_counter = 0
        #self._create_tables()
        self.completed_user_ids = []
        #self.refresh_completed_user_ids()


    def __del__(self):
        self.cursor.close()

    def construct_track_from_spotify(self, track_id: str) -> Track:
        sp_track = self.sp.track(track_id)
        return Track.from_spotify(track_id, sp_track)

    def construct_album_from_spotify(self, album_id: str) -> Album:
        sp_album = self.sp.album(album_id)
        return Album(sp_album_details=sp_album)

    def construct_artist_from_spotify(self, artist_id: str) -> Artist:
        sp_artist = self.sp.artist(artist_id)
        artist = Artist(sp_artist_details=sp_artist)
        artist.set_genres(sp_artist['genres'])
        offset = 0
        while True:
            sp_artist_albums = self.sp.artist_albums(artist_id, include_groups='album,single', limit=50, offset=offset)
            for sp_album in sp_artist_albums['items']:
                album_id = sp_album['id']
                #album = self.construct_album_from_spotify(album_id)
            if len(sp_artist_albums['items']) == 50:
                offset += 50
            else:
                break
        return artist

    def construct_playlist(self, playlist_id, sp_playlist_details=None) -> Playlist:
        sp_playlist_tracks = self.sp.playlist_tracks(playlist_id)
        return Playlist(playlist_id, sp_playlist_tracks, sp_playlist_details)




