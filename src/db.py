import sqlite3
import pandas as pd
from sqlite3 import Connection, Cursor
from .env import musicdb, audio_storage
from . import Track, Playlist, Album, Artist

def lookup_video_id(track_id: str, cursor):
    video_id = cursor.execute('''
    select video_id from audio_files where track_id = ?
                    ''', (track_id,)).fetchone()
    if video_id is None:
        return None
    else:
        return video_id[0]

def lookup_audio_path(track_id: str, cursor = None) -> str | None:
    cursor.execute("SELECT audio_path FROM audio_files WHERE track_id = ?", (track_id,))
    audio_path = cursor.fetchone()
    if audio_path:
        return audio_path[0]
    else:
        return None

def lookup_track_details(track_id: str, cursor) -> Track | None:
    cursor.execute("SELECT name, artist, album_id, popularity FROM tracks WHERE id = ?", (track_id,))
    track_details = cursor.fetchone()
    if track_details is not None:
        album_info = cursor.execute("SELECT name FROM albums WHERE id = ?", (track_details[2],)).fetchone()
        print(album_info)
        return Track(
            name = track_details[0],
            artist = track_details[1],
            album_id = track_details[2],
            album_name = album_info[0] if album_info is not None else None,
            popularity = track_details[3]
        )
    return None

def lookup_track(track_id: str, cursor: Cursor) -> Track | None:
    track = lookup_track_details(track_id, cursor)
    if track is not None:
        audio_path = lookup_audio_path(track_id, cursor)
        video_id = lookup_video_id(track_id, cursor)
        track["audio_path"] = audio_path
        track["video_id"] = video_id
        return track
    return None

def write_artist_to_db(artist: Artist, cursor: Cursor):
    cursor.execute('''
    INSERT OR IGNORE INTO artists (id, name)
    VALUES (?, ?)
    ''', (artist.id, artist.name))

def write_album_to_db(album: Album, cursor: Cursor):
    cursor.execute('''
    INSERT OR IGNORE INTO albums (id, name, artist_id, release_date, image_url)
    VALUES (?, ?, ?, ?, ?)
    ''', (album.id, album.name, album.artist_id, album.release_date, album.image_url))

def write_track_to_db(track: Track, cursor: Cursor):
    cursor.execute('''
    INSERT OR IGNORE INTO tracks (id, name, album_id, artist_id)
    VALUES (?, ?, ?, ?)
    ''', (track.id, track.name, track.album_id, track.artist_id))
    # below code is placeholder
    write_album_to_db(Album(track.album_id, track.album_name, track.artist_name, track.artist_id, track.release_date, track.image_url), cursor)
    write_artist_to_db(Artist(track.artist_name, track.artist_id), cursor)
    # write_audio_to_db(...)

    #cursor.execute('''
    #INSERT OR IGNORE INTO albums (id, name, artist_id, artist_name)
    #VALUES (?, ?, ?, ?)
    #''', (track.album_id, track.album_name, None, track.artist))

    #cursor.execute('''
    #INSERT OR IGNORE INTO audio_files (track_id, video_id, audio_path)
    #VALUES (?, ?, ?)
    #''', (track.id, track.video_id, track.audio_path))

#def write_playlist_to_db(playlist: Playlist, cursor: Cursor):
    #cursor.execute('''
    #INSERT OR IGNORE INTO playlists (id, name, description, owner_id, owner_name, total_tracks)
    #VALUES (?, ?, ?, ?, ?, ?)
    #''', (playlist.id, playlist.name, playlist.owner_id, playlist.owner_name, playlist.total_tracks))

    #for track_id, track in playlist.tracks.items():
        #write_track_to_db(track, cursor)

        #cursor.execute('''
        #INSERT OR IGNORE INTO playlist_tracks (playlist_id, track_id)
        #VALUES (?, ?)
        #''', (playlist.id, track_id))
        #cursor.commit()

def write_audio_to_db(track: Track, cursor: Cursor):
    if track.audio_path is None:
        print(f"track {track.id} has no video_id...")
    cursor.execute('''
    INSERT INTO audio_files (track_id, video_id, audio_path)
    VALUES (?, ?, ?)
    ON CONFLICT(track_id) DO UPDATE SET
    track_id = excluded.track_id,
    video_id = excluded.video_id,
    audio_path = excluded.audio_path;
    ''', (track.id, track.video_id, track.audio_path))

def connect_to_database(musicdb=musicdb) -> tuple[Connection, Cursor]:
    conn = sqlite3.connect(musicdb)
    cursor = conn.cursor()
    return conn, cursor

def create_tables():
    conn, cursor = connect_to_database()
    with open('./src/create_tables.sql', 'r') as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)

    conn.commit()
    conn.close()

def database_to_csv(output="./db.csv"):
    conn, cursor = connect_to_database()
    query = """
    SELECT
        t.id AS track_id,
        t.name AS track_name,
        t.artist_id,
        ar.name AS artist_name,
        t.album_id,
        al.name AS album_name,
        al.release_date,
        al.image_url,
        af.video_id,
        af.audio_path
    FROM tracks t
    LEFT JOIN artists ar ON t.artist_id = ar.id
    LEFT JOIN albums al ON t.album_id = al.id
    LEFT JOIN audio_files af ON t.id = af.track_id
    """

    df = pd.read_sql_query(query, conn)
    df.to_csv(output, index=False)
