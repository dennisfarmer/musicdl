import argparse
from argparse import ArgumentParser, RawTextHelpFormatter

from musicdl import TrackContainer
from musicdl.app import SpotifyInterface, YoutubeInterface, MusicDB
from platformdirs import user_cache_dir

class MusicDownloader:
    """
    ```
    mdl = MusicDownloader()
    track_url = "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU"
    track = mdl.from_url(track_url)
    ```
    """
    def __init__(self):
        self.spi = SpotifyInterface()
        self.yti = YoutubeInterface()
        self.db = MusicDB()

    def from_url(self, url: str, verbose=False) -> TrackContainer:
        """
        download YouTube audio using Spotify details at `url`, and save all information in `music.db`
        
        mp3 files are saved to `$AUDIO_STORAGE`, and referenced to in `music.db` via their absolute file path

        returns `Track`, `Album`, `Playlist`, or `Artist` object
        """
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

    class HelpFormatter(RawTextHelpFormatter):
        """
        custom formatter that inserts new line between args and allows multiline descriptions

        the default help formatter removes newline characters
        """
        def _split_lines(self, text, width):
            return super()._split_lines(text, width) + [""]

    hline = "----------------------------------------"
    parser = ArgumentParser(add_help=False, description="Download music audio from Youtube, using Spotify urls to obtain track info\nSupports tracks, albums, playlists, and artists", formatter_class=HelpFormatter)
    parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS,
                        help="\n".join([
                            "show this help message and exit",
                            "",
                            hline
                         ]))

    parser.add_argument("-u", dest="urls", nargs="*", default=None, 
                        help="\n".join([
                            "download mp3s using one or more Spotify urls",
                            "note: be sure to surround each url with double quotes",
                            "",
                            "musicdl -u \\",
                                '  "https://open.spotify.com/album/2YuS718NZa9vTJk9eoyD9B" \\',
                                '  "https://open.spotify.com/playlist/5E9bcB7cxoDOuT6zHcN2zB"',
                                "", 
                                hline
                        ]))
    parser.add_argument("-f", dest="file", nargs="?", default=None, type=str,
                        help="\n".join([
                            "download mp3s using a text file containing Spotify urls",
                            "",
                            "cat << EOF > example.txt",
                            '"https://open.spotify.com/artist/4A8byZgEqs8YRqUQ2HMmhA"',
                            '"https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU"',
                            "EOF", 
                            "", 
                            "musicdl -f example.txt",
                            "", 
                            hline
                            ]))
    parser.add_argument("--export", action="store_true", default=False,
                        help="\n".join([
                            "save music database to a CSV file for further processing",
                            "",
                            "musicdl --export",
                            "tree ./data",
                            "     ├── mp3s",
                            "     │   └── 10",
                            "     │       └── DonToliver_NoIdea_r-nPqWGG6c.mp3",
                            "     ├── music.db",
                            "     └── tracks.csv  <--",
                            "", 
                            hline
                            ]))

    parser.add_argument("--uninstall", default=False, action="store_true",
                        help=f"\n".join([
                            "uninstall musicdl's yt-dlp binary",
                            "",
                            "Equivalent to:",
                            f"  rm {user_cache_dir('musicdl')}/yt-dlp*",
                            f"  rmdir {user_cache_dir('musicdl')}",
                            "",
                            hline
                            ]))
    args = parser.parse_args()
    urls = args.urls
    file = args.file
    if args.export:
        db = MusicDB()
        db.to_csv(output_directory = "./data", single_file = True)
        exit(0)
    if args.uninstall:
        YoutubeInterface.uninstall_ytdlp()
        exit(0)
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

def main():
    urls = read_input()
    mdl = MusicDownloader()
    for url in urls:
        mdl.from_url(url, verbose=True)













