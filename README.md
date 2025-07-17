```bash
python -m venv .shazam_venv
source .shazam_venv/bin/activate
pip install -r requirements.txt
# create .env file with spotify client_id and client_secret (see .env_example)
```

```bash
python ./music_dl.py "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=0684264878094a00"
TrackInfo:
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

[![DonToliver_NoIdea_r-nPqWGG6c.mp3](https://img.youtube.com/vi/_r-nPqWGG6c/0.jpg)](https://www.youtube.com/watch?v=_r-nPqWGG6c)

```
./data
├── mp3s
│   └── 040
│       └── DonToliver_NoIdea_r-nPqWGG6c.mp3
├── music.db
└── tracks_full.csv
```

### `tracks_full.csv:`
|track_id|track_name|artist_id|artist_name|album_id|album_name|release_date|image_url|video_id|audio_path|
|:------:|:--------:|:-------:|:---------:|:------:|:--------:|:----------:|:-------:|:------:|:--------:|
|7AzlLxHn24DxjgQX73F9fU|No Idea|4Gso3d4CscCijv0lmajZWs|Don Toliver|7z4GhRfLqfSkqrj5F3Yt2B|Heaven Or Hell|2020-03-13|https://i.scdn.co/image/ab67616d0000b27345190a074bef3e8ce868b60c|_r-nPqWGG6c|./data/mp3s/040/DonToliver_NoIdea_r-nPqWGG6c.mp3|

generated via `mdl.to_csv(single_file=True)`



## TODO before July 19:
- finish downloader code for albums, playlists, and artists
- incorperate reading a text file with various track, album, playlist, and artist spotify urls