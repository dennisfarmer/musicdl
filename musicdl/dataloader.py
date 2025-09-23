import os
import zipfile
import pathlib

import pandas as pd

# zip file structure:
# tracks.zip:
# │
# ├── wav_files
# │   ├── song_1.wav
# │   ├── song_2.wav
# │   ├── ...
# │   └── song_n.wav
# └── tracks.csv

# tracks.csv:
#    youtube_url
#    title
#    artist
#    artwork_url
#    filename
#    duration_s

# filepaths are relative to where the tracks.csv file is located

def extract_zip(zipfile: str = "./tracks.zip", audio_directory: str = "./tracks"):
    # TODO: 
    # extract zip file to unique folder name (./tmp_0001/ or something)
    # move files to "audio_directory"
    # delete zip file
    pass

def create_zip(zipfile: str = "./tracks.zip", audio_directory: str = "./tracks"):
    # TODO:
    # compress audio_directory to a zip file with given filename
    pass

def load(audio_directory: str = "./tracks"):
    tracks_csv = pathlib.Path(audio_directory)/"tracks.csv"
    with open(tracks_csv, "r") as f:
        tracks_df = pd.read_csv(f)
        tracks_info = list(tracks_df.to_dict(orient="records"))
    # TODO: make sure filepaths work (convert to absolute paths?)
    return tracks_info
