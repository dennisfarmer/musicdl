# Package Installation:
```bash
git clone https://github.com/dennisfarmer/musicdl.git
python3 -m venv .venv && source .venv/bin/activate
pip3 install ./musicdl
```

```bash
# create a .musicdl_env file containing the following:
SPOTIFY_CLIENT_ID="your client id here"
SPOTIFY_CLIENT_SECRET="your client secret here"
```

## Spotify API Setup
- Create a [Spotify account](https://www.spotify.com/us/signup)
- Follow the [Getting started with Web API](https://developer.spotify.com/documentation/web-api/tutorials/getting-started) guide
    - Make sure that "Web API" is selected
    - Redirect URI: `https://example.com/callback`
- Add your credentials to `.musicdl_env`, located in the directory where `musicdl` is being used


# Overview:

```python
# ------------------------------------------------------------------------------
# the following line runs the code contained in src/musicdl/__main__.py:
# python3 -m musicdl -u "https://open.spotify.com/artist/4Gso3d4CscCijv0lmajZWs"
# ------------------------------------------------------------------------------

#!/usr/bin/env python 

from musicdl import MusicDownloader
from musicdl.dataloader import create_zip, extract_zip, load

mdl = MusicDownloader()
tracks_info = mdl.download([
                "https://www.youtube.com/watch?v=_r-nPqWGG6c"
                "https://open.spotify.com/album/0ESBFn4IKNcvgD53QJPlpD?si=PNFoDMvHTi6IaT6ia-s1Jw"
                "https://www.youtube.com/watch?v=37zCgCdV468"
                ])

# create_zip(zip_file="./tracks.zip", audio_directory="./tracks")
# extract_zip(zip_file="./tracks.zip", audio_directory="./tracks")

tracks_info = load(audio_directory = "./tracks")


```

```

tree ./tracks
#    ├── audios
#    │   ├── SeeingVoices1IntrotoSpectrograms.flac
#    │   │   ...
#    │   └── DonToliver_NoIdea_r-nPqWGG6c.flac
#    └── tracks.csv
```

[![DonToliver_NoIdea_r-nPqWGG6c.mp3](https://img.youtube.com/vi/_r-nPqWGG6c/0.jpg)](https://www.youtube.com/watch?v=_r-nPqWGG6c)

```
troubleshooting:
    403 Forbidden: use MusicDownloader(use_ytdlp_cli=True)
                   downloads cli version from github to user_cache_dir,
                   remove using musicdl.yt.uninstall_ytdlpcli()

    ffmpeg not found: default version uses a static version of ffmpeg 
                      from the ffmpeg-binaries package, should be fixed

    can't import modules:  use pip install ./musicdl, instead of
                           pip install -e ./musicdl

    vscode won't show documentation on hover:
                   add the following to .vscode/settings.json:
                      {
                        "python.analysis.extraPaths": [
                            "./musicdl"
                            ]
                      }

```
