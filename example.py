from musicdl.yt import YoutubeDownloader

def download_audio():
    ydl = YoutubeDownloader(audio_directory="./tracks", audio_format="wav")

    youtube_urls = [
        "https://www.youtube.com/watch?v=TqxfdNm4gZQ",
        "https://www.youtube.com/watch?v=MI_XU1iKRRc"
    ]

    tracks_info = ydl.download(youtube_urls)

    print(tracks_info)

    #[
        #{
            #'youtube_url': 'https://www.youtube.com/watch?v=TqxfdNm4gZQ', 
            #'title': 'Brad Mehldau - The Garden', 
            #'artist': 'Nonesuch Records', 
            #'artwork_url': 'https://i.ytimg.com/vi/TqxfdNm4gZQ/hqdefault.jpg', 
            #'audio_path': './tracks/BradMehldauTheGarden_NonesuchRecords.wav'
        #}, 
        #{
            #'youtube_url': 'https://www.youtube.com/watch?v=MI_XU1iKRRc', 
            #'title': 'King Gizzard and the Lizard Wizard - The River (Live on KEXP)', 
            #'artist': 'KEXP', 
            #'artwork_url': 'https://i.ytimg.com/vi/MI_XU1iKRRc/hqdefault.jpg', 
            #'audio_path': './tracks/KingGizzardandtheLizardWizardTheRiverLiveonKEXP_KEXP.wav'
        #}
    #]

def import_zip():
    pass

if __name__ == "__main__":
    download_audio()
    import_zip()