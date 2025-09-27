import os
import zipfile
import shutil
import pathlib

import pandas as pd

# zip file structure:
# tracks.zip:
# │
# ├── audio
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



def extract_zip(zip_file: str = "./tracks.zip", audio_directory: str = "./tracks"):
    """
    Extract `zip_file` to given `audio_directory`.

    If tracks already exist in `audio_directory`, this updates directory
    by adding tracks from `zip_file` to it
    """
    if os.path.exists(audio_directory):
        print(f"audio_directory={audio_directory} already exists")
    
    tmp_dir = pathlib.Path(audio_directory)/"tmp"
    os.makedirs(audio_directory, exist_ok=True)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        #zip_ref.extractall(audio_directory)
        files_in_zip = zip_ref.namelist()
        for file in files_in_zip:
            if file == "tracks.csv":
                zip_ref.extract(file, tmp_dir)
            else:
                print(file)
                zip_ref.extract(file, audio_directory)

    orig_csv = pathlib.Path(audio_directory)/"tracks.csv"
    orig_df = pd.read_csv(orig_csv)
    zip_df = pd.read_csv(tmp_dir/"tracks.csv")
    combined_df = pd.concat([orig_df, zip_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["youtube_url"])
    os.remove(orig_csv)
    combined_df.to_csv(orig_csv)

def create_zip(zip_file: str = "./tracks.zip", audio_directory: str = "./tracks"):
    """
    Compress `audio_directory` to a zip file located at `zip_file`.

    If `zip_file` already exists, deletes it.
    """
    try:
        if os.path.exists(zip_file):
            os.remove(zip_file)
        shutil.make_archive(os.path.splitext(zip_file)[0], "zip", audio_directory)
        return zip_file
    except FileNotFoundError as e:
        print(e)

def load(audio_directory: str = "./tracks"):
    """
    Retrieves list of track_info dictionaries from given `audio_directory`.
    """
    tracks_csv = pathlib.Path(audio_directory)/"tracks.csv"
    with open(tracks_csv, "r") as f:
        tracks_df = pd.read_csv(f)
        tracks_info = list(tracks_df.to_dict(orient="records"))
    # TODO: make sure filepaths work (convert to absolute paths?)
    return tracks_info
