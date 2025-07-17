class Track():
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
    def from_spotify(track_id, sp_track):
        # ensure we pass by value (copy the reference to a new object)
        track = sp_track.copy()
        # ensure we are indexed into the track_details dictionary
        if "track" in track:
            track = track["track"]
        assert track_id == track["id"]
        return Track(
            track_id=track_id,
            name=track["name"],
            artist_id=track["artists"][0]["id"],
            artist_name=track["artists"][0]["name"],
            album_id = track["album"]["id"],
            album_name = track["album"]["name"],
            image_url = track["album"]["images"][0]["url"],
            release_date = track["album"]["release_date"],
            video_id=None,
            audio_path=None
        )

    def __getitem__(self, key):
        return getattr(self, key)
    def __str__(self):
        #return f"{self.name} by {self.artist_name} - {self.id}\n{self.image_url}\n{self.release_date}"
        return f"""Track Info:
        id = {self.id}
        name = {self.name}
        artist_id = {self.artist_id}
        artist_name = {self.artist_name}
        album_id = {self.album_id}
        album_name = {self.album_name}
        image_url = {self.image_url}
        release_date = {self.release_date}
        video_id = {self.video_id}
        audio_path = {self.audio_path}"""


class Playlist():
    def __init__(self, playlist_id, sp_playlist_tracks):
        self.id = playlist_id
        self.tracks = {}
        for track in sp_playlist_tracks['items']:
            try: 
                track_id = track['track']['id']
            except TypeError:
                print("\t\tTrack has been removed from Spotify, skipping...")
                continue
            self.tracks[track_id] = Track.from_spotify(track_id, track)

    @staticmethod
    def url_to_id(sp_playlist_url: str) -> str:
        import re
        match = re.search(r'playlist/([a-zA-Z0-9]+)', sp_playlist_url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid playlist URL")

class Album():
    def __init__(self, album_name: str = None, album_id: str = None, artist_name: str = None, artist_id: str = None, release_date: str = None, image_url: str = None, sp_album_details: dict = None, tracks: dict[str, Track] = None):
        if sp_album_details is None:
            self.name = album_name
            self.id = album_id
            self.artist_id = artist_id
            self.artist_name = artist_name
            self.release_date = release_date
            self.image_url = image_url
            self.tracks = tracks
        elif sp_album_details is not None:
            self.name = sp_album_details["name"]
            self.id = sp_album_details['id']
            self.artist_id = sp_album_details["artists"][0]["id"]
            self.artist_name = sp_album_details["artists"][0]["name"]
            self.release_date = sp_album_details["release_date"]
            self.album_type = sp_album_details["album_type"]
            self.tracks = {}
            for track in sp_album_details['tracks']['items']:
                track_id = track['id']
                self.tracks[track_id] = Track.from_spotify(track_id, track, album={"name": self.name, "id": self.id})

    def __str__(self):
        s = f"{self.name} by {self.artist} ({self.release_date}) - {self.id}"
        for track in self.tracks.values():
            s += f"\n\t\t{track}"
        return s

class Artist():
    def __init__(self, artist_name: str = None, artist_id: str = None):
        self.albums = {}
        self.name = artist_name
        self.id = artist_id

    def __str__(self):
        return f"{self.name} - {self.id}"
