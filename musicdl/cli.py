import os
import re
import zipfile

import pandas as pd
import argparse
from argparse import ArgumentParser, RawTextHelpFormatter
from platformdirs import user_cache_dir
from tqdm import tqdm

from .containers import Track, TrackContainer, update_csv
from .sp import SpotifyInterface
from .yt import YoutubeDownloader, SPTrackDownloader, uninstall_ytdlpcli
from .db import MusicDB
from .config import config

class MusicDownloader:
    """
    ```
    mdl = MusicDownloader()
    track_url = "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU"
    track = mdl.download(track_url)
    ```
    `use_db = True`: optionally save all information in `music.db` using SQLite if `use_db` is True, for keeping a structured database of songs.
    
    `use_ytdlp_cli = False`: (default) use Python version of yt-dlp, with static version of ffmpeg installed via pip 

    `use_ytdlp_cli = True`: Optional download yt-dlp from github, seems less prone to 403 Forbidden errors (installs to user cache)
    """
    def __init__(self, audio_directory = None, audio_format = None, use_db = False, use_ytdlp_cli = False):
        if audio_directory is None:
            audio_directory = config["datadir"]
        if audio_format is None:
            audio_format = "wav"
        self.audio_directory = audio_directory
        self.audio_format = audio_format
        self.use_db = use_db
        self.db = MusicDB() if use_db else None
        self.sp = SpotifyInterface()
        self.yt_cli = SPTrackDownloader(
            self.db.conn.cursor() if self.db is not None else None, 
            audio_format=audio_format, ytdlp_version="cli" if use_ytdlp_cli else "py")
        self.yt = YoutubeDownloader(audio_directory=audio_directory, audio_format=audio_format, 
                                    use_ytdlp_cli=use_ytdlp_cli)

    def download(self, urls: list[str], verbose=True) -> list[dict]:
        """
        download YouTube audio using Spotify details at each url in `urls`, 
        
        returns `Track`, `Album`, `Playlist`, or `Artist` object
        """
        output_list = []
        for url in tqdm(urls, desc="Downloading from urls"):
            if "spotify" in url:
                tc = self.sp.retrieve_track_container(url)
                tc = self.yt_cli.add_audio(tc, verbose=verbose)
                if self.use_db: 
                    self.db.add(tc)
                if verbose: 
                    print(tc)
                tracks_info = tc.to_list()
            else:
                if "&list=" in url:
                    print(url)
                    print("musicdl does not currently support youtube playlists")
                    print("converted to single url (removing &list=...)")
                    url = re.match("^(.*)&list=", url).group(1)
                tracks_info = self.yt.download([url])
                # note: does not store youtube urls into db
                #       use spotify urls to get pretty album art
                # note: update_csv runs in yt.download()

            update_csv(os.path.join(self.audio_directory, "tracks.csv"), tracks_info)
            output_list.extend(tracks_info)
        return output_list

    def to_csv(self, tracks_info: list[dict] = None) -> str|list[str]:
        """
        save info about tracks in `tracks_info` to a csv file

        if csv already exists, this updates it by appending tracks
        in `tracks_info` to it
        """
        if self.use_db:
            return self.db.to_csv()
        else:
            tracks_info_csv = os.path.join(self.audio_directory, "tracks.csv")
            if os.path.exists(tracks_info_csv):
                orig_df = pd.read_csv(tracks_info_csv)
                new_df = pd.DataFrame(tracks_info)
                combined_df = pd.concat([orig_df, new_df], ignore_index=True)
                combined_df = combined_df.drop_duplicates(subset=["youtube_url"])
                os.remove(tracks_info_csv)
                combined_df.to_csv(tracks_info_csv, index=False)
            else:
                os.remove(tracks_info_csv)
                new_df = pd.DataFrame(tracks_info)
                new_df.to_csv(tracks_info_csv, index=False)
            return tracks_info_csv

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

        print(f"audios and track info saved to {os.path.abspath(dest_zip)}")

    def close(self):
        if self.use_db:
            self.db.close()
    
    def __del__(self):
        self.close()

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
                            "download audios using one or more Spotify urls",
                            "",
                            "musicdl -u \\",
                                '  "https://open.spotify.com/album/2YuS718NZa9vTJk9eoyD9B" \\',
                                '  "https://open.spotify.com/playlist/5E9bcB7cxoDOuT6zHcN2zB"',
                                "", 
                                hline
                        ]))
    parser.add_argument("-f", dest="file", nargs="?", default=None, type=str,
                        help="\n".join([
                            "download audio using a text file containing Spotify urls",
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
                            f">> audios and track info saved to: ./{config['zip']()}",
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
        mdl = MusicDownloader(use_db=True)
        mdl.to_zip()
        mdl.close()
        exit(0)
    if args.uninstall:
        uninstall_ytdlpcli()
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
    mdl = MusicDownloader(use_db=True)
    mdl.download(urls, verbose=True)
    mdl.close()
