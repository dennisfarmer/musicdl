from dotenv import dotenv_values, find_dotenv
import warnings
import sys
import os

def load_config(dotenv_path: str = None):
    if dotenv_path is not None and not os.path.exists(dotenv_path):
        dotenv_path = os.path.abspath(dotenv_path)
        warnings.warn(f"Note: {dotenv_path} does not exist")
        dotenv_path = find_dotenv(filename=".env", usecwd=True)
        if dotenv_path != "":
            warnings.warn(f"using {dotenv_path}")
        else:
            warnings.warn("using enviroment variables")
    elif dotenv_path is None:
        dotenv_path = find_dotenv(filename=".env", usecwd=True)
    dotenv_path = os.path.abspath(dotenv_path)
    env = dotenv_values(dotenv_path)

    config = {
        # https://developer.spotify.com/documentation/web-api/tutorials/getting-started
        "client_id": env.get("SPOTIFY_CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID"),
        "client_secret": env.get("SPOTIFY_CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET"),

        # specify the path of the sqlite database file
        "music_db": env.get("MUSIC_DB") or os.getenv("MUSIC_DB") or "./data/music.db",

        # specify the directory where the downloaded mp3 files should be stored
        "mp3_storage": env.get("MP3_STORAGE") or os.getenv("MP3_STORAGE") or "./data/mp3s",

        # specify the directory where the exported CSV file(s) should be stored
        "csv_storage": env.get("CSV_STORAGE") or os.getenv("CSV_STORAGE") or "./data",

        # split the storing of mp3s into multiple directories (True/False)
        # $MP3_STORAGE
        # ├── 01
        # ├── 02
        # ├── 03
        # ├── 04
        # ├── 05
        # ├── 06
        # ├── 07
        # ├── 08
        # ├── 09
        # └── 10
        "hash_mp3_storage": env.get("HASH_MP3_STORAGE") or "True"
    }
    client_id, client_secret = config.get("client_id"), config.get("client_secret")
    if client_id is None or client_secret is None or client_id == "" or client_secret == "":
        print("\n".join([f"Spotify API Credentials not found in {dotenv_path} or in environment variables",
                         "Please provide SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET",
                         "https://developer.spotify.com/documentation/web-api/tutorials/getting-started"
                         ]))
        exit(1)
    
    config["hash_mp3_storage"] = config["hash_mp3_storage"] == "True"

    return config

config: dict[str, str] = load_config()
