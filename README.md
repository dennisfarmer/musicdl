# Installation

```bash
git clone https://github.com/dennisfarmer/musicdl.git
cd musicdl
python3 -m venv .venv && source .venv/bin/activate
pip3 install -e .
# create .env file with spotify client_id and client_secret (see .env_example)
```

# How to Use

```
usage: musicdl [-h] [-u [URLS ...]] [-f [FILE]] [--uninstall]

Download music audio from Youtube, using Spotify urls to obtain track info
Supports tracks, albums, playlists, and artists

---------------------------------------------------------

  -h, --help     show this help message and exit
                 
---------------------------------------------------------
                 
  -u [URLS ...]  download mp3s using one or more Spotify urls
                 note: be sure to surround each url with double quotes
                 
                 Example:
                 musicdl -u \
                   "https://open.spotify.com/album/2YuS718NZa9vTJk9eoyD9B?si=a6BbX_G2TPKyrTnXniafuQ" \
                   "https://open.spotify.com/playlist/5E9bcB7cxoDOuT6zHcN2zB?si=b43d397f80c34746"
                 
---------------------------------------------------------
                 
  -f [FILE]      download mp3s using a text file containing Spotify urls
                 
                 Example:
                 cat << EOF > example.txt
                 "https://open.spotify.com/artist/4A8byZgEqs8YRqUQ2HMmhA?si=771plXN7SqeYgfBEvCq4kw"
                 "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=0684264878094a00"
                 EOF
                 
                 musicdl -f example.txt
                 
---------------------------------------------------------
                 
  --uninstall    uninstall musicdl's yt-dlp binary
                 
                 Equivalent to:
                   rm /Users/dennisfj/Library/Caches/musicdl/yt-dlp*
                   rmdir /Users/dennisfj/Library/Caches/musicdl
                 
---------------------------------------------------------
```
```
Track - No Idea by Don Toliver (2020-03-13) - 7AzlLxHn24DxjgQX73F9fU
        artist_id = 4Gso3d4CscCijv0lmajZWs
        album_id = 7z4GhRfLqfSkqrj5F3Yt2B
        album_name = Heaven Or Hell
        image_url = https://i.scdn.co/image/ab67616d0000b27345190a074bef3e8ce868b60c
        release_date = 2020-03-13
        video_id = _r-nPqWGG6c
        audio_path = ./data/mp3s/10/DonToliver_NoIdea_r-nPqWGG6c.mp3
```

[![DonToliver_NoIdea_r-nPqWGG6c.mp3](https://img.youtube.com/vi/_r-nPqWGG6c/0.jpg)](https://www.youtube.com/watch?v=_r-nPqWGG6c)

```
./data
├── mp3s
│   └── 10
│       └── DonToliver_NoIdea_r-nPqWGG6c.mp3
├── music.db
└── tracks.csv
```

### `music.db`
![ER Diagram](er_diagram.png)

### `tracks.csv`
|track_id|track_name|artist_id|artist_name|album_id|album_name|release_date|image_url|video_id|audio_path|
|:------:|:--------:|:-------:|:---------:|:------:|:--------:|:----------:|:-------:|:------:|:--------:|
|7AzlLxHn24DxjgQX73F9fU|No Idea|4Gso3d4CscCijv0lmajZWs|Don Toliver|7z4GhRfLqfSkqrj5F3Yt2B|Heaven Or Hell|2020-03-13|https://i.scdn.co/image/ab67616d0000b27345190a074bef3e8ce868b60c|_r-nPqWGG6c|./data/mp3s/10/DonToliver_NoIdea_r-nPqWGG6c.mp3|

# Uninstall

`musicdl` installs yt-dlp to your user cache directory. To uninstall it, run the following

```bash
# removes musicdl folder from user cache directory
# located at `platformdirs.user_cache_dir("musicdl")`
musicdl --uninstall
```