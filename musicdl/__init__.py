import platform
import abc
import sys
import os

class TrackContainer(abc.ABC):
    """
    Abstract Base Class representing a Track, Album, Playlist, or Artist
    """
    @abc.abstractmethod
    def __init__(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def from_spotify():
        pass

    @abc.abstractmethod
    def __getitem__(self, key):
        return getattr(self, key)

    @abc.abstractmethod
    def __str__():
        pass


class Track(TrackContainer):
    def __init__(self, track_id: str, name: str, artist_id: str, artist_name: str, album_id: str, album_name: str, image_url: str, release_date: str, video_id: str = None, audio_path: str = None):
        self.id = track_id
        self.name = name
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.album_id = album_id
        self.album_name = album_name
        self.image_url = image_url
        self.release_date = release_date
        self.video_id = video_id
        self.audio_path = audio_path

    @staticmethod
    def from_spotify(track_id, sp_track, album=None):
        sp_track_details = sp_track.copy()
        if "track" in sp_track_details:
            sp_track_details = sp_track_details["track"]
        assert track_id == sp_track_details["id"]
        if album is None:
            album_name = sp_track_details["album"]["name"]
            album_id = sp_track_details["album"]["id"]
            image_url = sp_track_details["album"]["images"][0]["url"]
            release_date = sp_track_details["album"]["release_date"]
        else:
            album_name = album.name
            album_id = album.id
            image_url = album.image_url
            release_date = album.release_date
        return Track(
            track_id=track_id,
            name=sp_track_details["name"],
            artist_id=sp_track_details["artists"][0]["id"],
            artist_name=sp_track_details["artists"][0]["name"],
            album_id = album_id,
            album_name = album_name,
            image_url = image_url,
            release_date = release_date,
            video_id=None,
            audio_path=None
        )

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        s = f"Track - {self.name} by {self.artist_name} ({self.release_date}) - {self.id}"
        s += f"\n\tartist_id = {self.artist_id}"
        s += f"\n\talbum_id = {self.album_id}"
        s += f"\n\talbum_name = {self.album_name}"
        s += f"\n\timage_url = {self.image_url}"
        s += f"\n\trelease_date = {self.release_date}"
        s += f"\n\tvideo_id = {self.video_id}"
        s += f"\n\taudio_path = {self.audio_path}"
        return s

class Album(TrackContainer):
    def __init__(self, album_name: str = None, album_id: str = None, artist_name: str = None, artist_id: str = None, release_date: str = None, image_url: str = None, tracks: dict[str, Track] = None):
        self.name = album_name
        self.id = album_id
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.release_date = release_date
        self.image_url = image_url
        self.tracks = tracks

    @staticmethod
    def from_spotify(album_id, sp_album):
        sp_album_details = sp_album.copy()
        assert album_id == sp_album_details["id"]
        album = Album(
            album_name = sp_album_details["name"],
            album_id = sp_album_details['id'],
            artist_name = sp_album_details["artists"][0]["name"],
            artist_id = sp_album_details["artists"][0]["id"],
            release_date = sp_album_details["release_date"],
            image_url = sp_album_details["images"][0]["url"],
            tracks = {}
        )
        for track in sp_album_details['tracks']['items']:
            track_id = track['id']
            album.tracks[track_id] = Track.from_spotify(track_id, track, album)
        return album

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        s = f"Album - {self.name} by {self.artist_name} ({self.release_date}) - {self.id}"
        for i, track in enumerate(self.tracks.values()):
            s += f"\n\t{i+1}. {track.name}"
        return s

class Playlist(TrackContainer):
    def __init__(self, playlist_id: str, tracks: dict[str, Track]):
        self.id = playlist_id
        self.tracks: dict[str, Track] = tracks

    @staticmethod
    def from_spotify(playlist_id, sp_playlist_tracks):
        playlist = Playlist(
            playlist_id = playlist_id,
            tracks = {}
        )
        for track in sp_playlist_tracks['items']:
            try: 
                track_id = track['track']['id']
            except TypeError:
                print("\t\tTrack has been removed from Spotify, skipping...")
                continue
            playlist.tracks[track_id] = Track.from_spotify(track_id, track)
        return playlist

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        s = f"Playlist - {self.id}"
        for i, track in enumerate(self.tracks.values()):
            s += f"\n\t{i+1}. {track.name}"
        return s

class Artist(TrackContainer):
    def __init__(self, artist_name: str = None, artist_id: str = None):
        self.name = artist_name
        self.id = artist_id
        self.albums: dict[str, Album] = {}

    @staticmethod
    def from_spotify():
        raise NotImplementedError("use `SpotifyInterface.retrieve_artist(artist_id)` to retrieve artist tracks")

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        s = f"Artist - {self.name} - {self.id}"
        for i, album in enumerate(self.albums.values()):
            s += f"\n\t{i+1}. {album.name} ({album.release_date})"
            for j, track in enumerate(album.tracks.values()):
                s += f"\n\t\t{j+1}. {track.name}"
        return s
