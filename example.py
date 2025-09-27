from musicdl.dataloader import *
from musicdl.yt import YoutubeDownloader
from musicdl.mdl import MusicDownloader
import pandas as pd
from pathlib import Path

def download_audio():
    ydl = YoutubeDownloader(audio_directory="./tracks", audio_format="wav")

    youtube_urls = [
        #"https://www.youtube.com/watch?v=TqxfdNm4gZQ",
        #"https://www.youtube.com/watch?v=MI_XU1iKRRc"
    ]

    tracks_info = ydl.download(youtube_urls)
    # print(tracks_info)
    #[
        #{
            #'youtube_url': 'https://www.youtube.com/watch?v=TqxfdNm4gZQ', 
            #'title': 'Brad Mehldau - The Garden', 
            #'artist': 'Nonesuch Records', 
            #'artwork_url': 'https://i.ytimg.com/vi/TqxfdNm4gZQ/hqdefault.jpg', 
            #'audio_path': './audio/BradMehldauTheGarden_NonesuchRecords.wav'
        #}, 
        #{
            #'youtube_url': 'https://www.youtube.com/watch?v=MI_XU1iKRRc', 
            #'title': 'King Gizzard and the Lizard Wizard - The River (Live on KEXP)', 
            #'artist': 'KEXP', 
            #'artwork_url': 'https://i.ytimg.com/vi/MI_XU1iKRRc/hqdefault.jpg', 
            #'audio_path': './audio/sKingGizzardandtheLizardWizardTheRiverLiveonKEXP_KEXP.wav'
        #}
    #]

    return tracks_info

urls_hello_meteor = [
        "https://www.youtube.com/watch?v=5K6fO9Bdlgg",
        "https://www.youtube.com/watch?v=CI2Oa1Ds6Z8",
        "https://www.youtube.com/watch?v=iVzXMytwCCo",
        "https://www.youtube.com/watch?v=THV2TDARpS0",
        "https://www.youtube.com/watch?v=MXtQ5I0asKg",
        "https://open.spotify.com/album/0ESBFn4IKNcvgD53QJPlpD?si=PNFoDMvHTi6IaT6ia-s1Jw"
]

if __name__ == "__main__":
    mdl = MusicDownloader(audio_directory="./tracks_mp3", audio_format = "mp3", use_ytdlp_cli = True)
    #youtube_urls = [
        #"https://www.youtube.com/watch?v=MI_XU1iKRRc",
    #]
    mdl.download(urls_hello_meteor)
    #extract_zip("./tracks_hello_meteor.zip")
    create_zip(zip_file="./tracks_mp3.zip", audio_directory="./tracks_mp3")


    #tracks_info = download_audio()
    #tracks_df = pd.DataFrame(tracks_info)
    #tracks_df.to_csv("./tracks/tracks.csv")