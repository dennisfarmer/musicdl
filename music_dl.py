from argparse import ArgumentParser
from src import Track, Album, Playlist, Artist
from src.add_music import SpotifyInterface, YoutubeInterface
from src.db import MusicDB

class MusicDownloader:
    """
    ```
    mdl = MusicDownloader()
    track_url = "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=0684264878094a00"
    track_id = mdl.parse_url(track_url)
    track = mdl.download_track(track_id)
    ```
    """
    def __init__(self, urls=None):
        self.spi = SpotifyInterface()
        self.yti = YoutubeInterface()
        self.db = MusicDB()
        self.urls = urls
        self.idx = 0 if self.urls is not None else None

    def download_from_url(self, url) -> Track|Album|Playlist|Artist:
        _id, id_type = self.parse_url(url)
        self.idx += 1
        if id_type == "track":
            return self.download_track(_id)
        elif id_type == "album":
            return self.download_album(_id)
        elif id_type == "playlist":
            return self.download_playlist(_id)
        elif id_type == "artist":
            return self.download_artist(_id)

    def download_track(self, track_id) -> Track|None:
        try:
            track = self.spi.retrieve_track(track_id)
            self.yti.add_audio(track)
            self.db.add_track(track)
            return track
        except:
            return None

    def download_album(self, album_id) -> Album|None:
        try:
            album = Album()
            return album
        except:
            return None

    def download_playlist(self, playlist_id) -> Playlist|None:
        try:
            playlist = Playlist()
            return playlist
        except:
            return None

    def download_artist(self, artist_id) -> Artist|None:
        try:
            artist = Artist()
            return artist
        except:
            return None

    def parse_url(self, url):
        return self.spi.parse_url(url)

    def to_csv(self, output_directory="./data", single_file=True):
        self.db.to_csv(output_directory, single_file)

    def close(self):
        self.db.close()

    def _process_single_url(self) -> Track|Album|Playlist|Artist:
        assert self.urls is not None
        if self.idx >= len(self.urls) or self.idx < 0:
            return False, ""
        item = self.download_from_url(self.urls[self.idx])
        self.idx += 1
        return item

    def process_cmdline_args(self, verbose=False) -> list[Track|Album|Playlist|Artist]:
        items = []
        self.idx = 0
        for _ in range(len(self.urls)):
            item = self._process_single_url()
            if verbose: print("success" if item is not None else f"failure")
            items.append(item)
        return items
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("urls", nargs="*")
    urls = parser.parse_args().urls

    mdl = MusicDownloader(urls)
    results = mdl.process_cmdline_args()
    print(results[0])

    output_csv = mdl.to_csv(single_file=True)