```bash
python3 -m venv .shazam_venv
source .shazam_venv/bin/activate
python3 -m pip install -r requirements.txt
# create .env file with spotify client_id and client_secret (see .env_example)

# currently only supports spotify track urls:
python3 dlmusic.py "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=52bf843ef71e40d9"
```

```
Track Info:
        id = 7AzlLxHn24DxjgQX73F9fU
        name = No Idea
        artist_id = 4Gso3d4CscCijv0lmajZWs
        artist_name = Don Toliver
        album_id = 7z4GhRfLqfSkqrj5F3Yt2B
        album_name = Heaven Or Hell
        image_url = https://i.scdn.co/image/ab67616d0000b27345190a074bef3e8ce868b60c
        release_date = 2020-03-13
        video_id = _r-nPqWGG6c
        audio_path = ./data/mp3s/040/DonToliver_NoIdea_r-nPqWGG6c.mp3
```


## TODO:
- finish downloader code for albums, playlists, and artists
- incorperate reading a text file with various track, album, playlist, and artist spotify urls