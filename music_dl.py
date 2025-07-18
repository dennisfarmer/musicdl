from argparse import ArgumentParser
from src import Track, Album, Playlist, Artist
from src.add_music import SpotifyInterface, YoutubeInterface
from src.db import MusicDB

class MusicDownloader:
    """
    ```
    mdl = MusicDownloader()
    track_url = "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=0684264878094a00"
    track = mdl.from_url(track_url)
    ```
    """
    def __init__(self):
        self.spi = SpotifyInterface()
        self.yti = YoutubeInterface()
        self.db = MusicDB()

    def from_url(self, url: str, verbose=False) -> Track|Album|Playlist|Artist:
        tc = self.spi.retrieve_track_container(url)
        self.yti.add_audio(tc)
        self.db.add(tc)
        if verbose: print(tc)
        return tc

    def to_csv(self, output_directory="./data", single_file=True) -> str|list[str]:
        return self.db.to_csv(output_directory, single_file)

    def close(self):
        self.db.close()

def read_input():
    """
    handle command line arguments and return a list of urls to be processed
    """
    parser = ArgumentParser()
    parser.add_argument("--file", "-f", dest="file", help="Text file containing Spotify urls (one per line)", nargs="?", default=None, type=str)
    parser.add_argument("--urls", "-u", dest="urls", help="One or more Spotify urls, each surrounded with double quotes", nargs="*", default=None)
    args = parser.parse_args()
    urls = args.urls
    file = args.file
    # combine urls from --file and --urls into single list
    if file is not None:
        with open(file, "r") as f:
            file_urls = [line.strip() for line in f if line.strip()]
        if urls is not None:
            file_urls.append(urls)
        urls = file_urls
    if urls is None:
        print("no arguments specified, see --help for details")
        exit(0)
    # some terminals automatically escape certain characters (such as '?') when pasting
    return [url.replace("\\", "") for url in urls]

if __name__ == "__main__":
    urls = read_input()

    mdl = MusicDownloader()
    for url in urls:
        tc = mdl.from_url(url, verbose=True)

    output_csv = mdl.to_csv(single_file=True)