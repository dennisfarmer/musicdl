import os
import sys
import platform
from dotenv import dotenv_values

env = dotenv_values(os.path.join(sys.path[0],".env"))

client_id = env["SPOTIPY_CLIENT_ID"]
client_secret = env["SPOTIPY_CLIENT_SECRET"]

musicdb = env["MUSIC_DB"]
audio_storage = env["AUDIO_STORAGE"]
yt_dlp = env["YT_DLP"]
