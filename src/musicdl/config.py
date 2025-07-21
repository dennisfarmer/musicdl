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
        "client_id": env.get("SPOTIPY_CLIENT_ID") or os.getenv("SPOTIPY_CLIENT_ID"),
        "client_secret": env.get("SPOTIPY_CLIENT_SECRET") or os.getenv("SPOTIPY_CLIENT_SECRET"),
        "music_db": env.get("MUSIC_DB") or os.getenv("MUSIC_DB") or "./data/music.db",
        "audio_storage": env.get("AUDIO_STORAGE") or os.getenv("AUDIO_STORAGE") or "./data/mp3s"
    }
    if config.get("client_id") is None or config.get("client_secret") is None:
        print(f"Spotify API Credentials not found in {dotenv_path} or in environment variables\nPlease provide SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET\nSee https://developer.spotify.com/documentation/web-api/tutorials/getting-started for details")
        exit(1)

    config["hash_audio_path"] = False

    return config

config: dict[str, str] = load_config()
