from argparse import ArgumentParser
from src.add_music import *
from src.db import create_tables, connect_to_database, database_to_csv, write_track_to_db

def download_track(url):
    spi = SpotifyInterface()
    track_id = url.split("/track/")[1].split("?")[0]
    track = spi.construct_track(track_id)
    track.video_id = search_yt_for_video_id(track)
    track.audio_path = download_audio(track.artist_name, track.name, track.video_id)

    create_tables()
    conn, cursor = connect_to_database(musicdb)
    write_track_to_db(track, cursor)
    conn.commit()
    print(track)

    cursor.close()

def download_album(url):
    spi = SpotifyInterface()
    album_id = url.split("/album/")[1].split("?")[0]
    pass

def download_playlist(url):
    spi = SpotifyInterface()
    playlist_id = url.split("/playlist/")[1].split("?")[0]
    pass

def download_artist(url):
    spi = SpotifyInterface()
    artist_id = url.split("/artist/")[1].split("?")[0]
    pass
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("urls", nargs="*")
    urls = parser.parse_args().urls
    

    # "https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=52bf843ef71e40d9"
    # "https://open.spotify.com/album/3apDacETcGFurMaKWAuxG9?si=38a1839ea5fd4375"

    for url in urls:
    # test 1: download track
        if "track" in url:
            download_track(url)

    ## test 2: download album
        #elif "album" in url:
            #download_album(url)

    ## test 3: download playlist
        #elif "playlist" in url:
            #download_playlist(url)

    ## test 4: download artist
        #elif "artist" in url:
            #download_artist(url)

    database_to_csv(output="./db.csv")