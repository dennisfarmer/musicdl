import os
import zipfile

import pandas as pd
import argparse
from argparse import ArgumentParser, RawTextHelpFormatter
from platformdirs import user_cache_dir

from musicdl import Track, TrackContainer
from musicdl.app import SpotifyInterface, YoutubeInterface, MusicDB
from musicdl.config import config

class MusicDownloader:
    """
    ```
    mdl = MusicDownloader()
    track_url = "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU"
    track = mdl.from_url(track_url)
    mdl.close()
    ```
    """
    def __init__(self):
        self.db = MusicDB()
        self.spi = SpotifyInterface(self.db.conn.cursor())
        self.yti = YoutubeInterface(self.db.conn.cursor())

    def from_url(self, url: str, verbose=True) -> TrackContainer:
        """
        download YouTube audio using Spotify details at `url`, and save all information in `music.db`
        
        returns `Track`, `Album`, `Playlist`, or `Artist` object
        """
        tc = self.spi.retrieve_track_container(url)
        tc = self.yti.add_audio(tc, verbose=verbose)
        self.db.add(tc)
        if verbose: print(tc)
        return tc

    def to_csv(self) -> str|list[str]:
        return self.db.to_csv()
    
    def from_csv(self, csv="./data/tracks.csv"):
        col_names = [
            "track_id", "track_name", "artist_id", "artist_name",
            "album_id", "album_name", "release_date", "image_url",
            "video_id", "audio_path"
        ]
        df = pd.read_csv(csv, names=col_names, header=0)
        for _, row in df.iterrows():
            track = Track(
                track_id=row["track_id"],
                name=row["track_name"],
                artist_id=row["artist_id"],
                artist_name=row["artist_name"],
                album_id=row["album_id"],
                album_name=row["album_name"],
                image_url=row["image_url"],
                release_date=row["release_date"],
                video_id=row["video_id"],
                audio_path=row["audio_path"]
            )


            self.db._insert_track(track)
    

    def to_zip(self):
        csv_path = self.to_csv()
        db_filename = os.path.basename(config["music_db"])

        source_dir = config["datadir"]
        dest_zip = config["zip"]()
        if os.path.exists(dest_zip):
            os.remove(dest_zip)
        with zipfile.ZipFile(dest_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file == db_filename:
                        continue
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

        print(f"mp3s and track info saved to {os.path.abspath(dest_zip)}")

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
                            "save music to a ZIP file for further processing",
                            "",
                            "musicdl --export",
                            f">> mp3s and track info saved to: ./{config["zip"]()}",
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
        mdl = MusicDownloader()
        mdl.to_zip()
        mdl.close()
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
    mdl.close()













