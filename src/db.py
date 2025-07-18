import sqlite3
import pandas as pd
from sqlite3 import Connection, Cursor
from .env import music_db
from . import Track, Playlist, Album, Artist, TrackContainer
import os

class MusicDB:
    def __init__(self, musicdb=music_db):
        self.musicdb = musicdb
        self.conn=None
        self.cursor=None
        self.connect_to_database()

    def _insert_track(self, track: Track):
        self.cursor.execute('''
        INSERT OR IGNORE INTO tracks (id, name, album_id, artist_id)
        VALUES (?, ?, ?, ?)
        ''', (track.id, track.name, track.album_id, track.artist_id))

        self.cursor.execute('''
        INSERT OR IGNORE INTO artists (id, name)
        VALUES (?, ?)
        ''', (track.artist_id, track.artist_name))

        self.cursor.execute('''
        INSERT OR IGNORE INTO albums (id, name, artist_id, release_date, image_url)
        VALUES (?, ?, ?, ?, ?)
        ''', (track.album_id, track.album_name, track.artist_id, track.release_date, track.image_url))

        self.cursor.execute('''
        INSERT INTO audio_files (track_id, video_id, audio_path)
        VALUES (?, ?, ?)
        ON CONFLICT(track_id) DO UPDATE SET
        track_id = excluded.track_id,
        video_id = excluded.video_id,
        audio_path = excluded.audio_path;
        ''', (track.id, track.video_id, track.audio_path))

    def _insert_collection(self, c: Album|Playlist):
        for track in c.tracks.values():
            self._insert_track(track)

    def add(self, tc: TrackContainer):
        assert isinstance(tc, TrackContainer)
        if isinstance(tc, Track):
            self._insert_track(tc)
        elif isinstance(tc, Album) or isinstance(tc, Playlist):
            self._insert_collection(tc)
        elif isinstance(tc, Artist):
            for album in tc.albums.values():
                self._insert_collection(album)

    def connect_to_database(self, musicdb=None) -> tuple[Connection, Cursor]:
        if musicdb is not None:
            self.musicdb = musicdb
        basedir = os.path.dirname(os.path.abspath(self.musicdb))
        os.makedirs(basedir, exist_ok=True)
        self.conn = sqlite3.connect(self.musicdb)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        sql_script = """
        CREATE TABLE IF NOT EXISTS artists (
            id TEXT PRIMARY KEY,
            name TEXT
        );

        CREATE TABLE IF NOT EXISTS albums (
            id TEXT PRIMARY KEY,
            name TEXT,
            artist_id TEXT,
            release_date TEXT,
            image_url TEXT,
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        );

        CREATE TABLE IF NOT EXISTS tracks (
            id TEXT PRIMARY KEY,
            name TEXT,
            album_id TEXT,
            artist_id TEXT,
            FOREIGN KEY (album_id) REFERENCES albums(id),
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        );

        CREATE TABLE IF NOT EXISTS audio_files (
            track_id TEXT PRIMARY KEY,
            video_id TEXT,
            audio_path TEXT,
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        );
        """
        self.cursor.executescript(sql_script)
    
    def reset_database(self):
        if os.path.exists(self.musicdb):
            os.remove(self.musicdb)
        self.connect_to_database()

    def close(self):
        self.conn.close()

    def to_csv(self, output_directory="./data", single_file=True) -> str|list[str]:
        for file in os.listdir(output_directory):
            if file.endswith(".csv"):
                os.remove(os.path.join(output_directory, file))
        if single_file:
            query = """
            SELECT
                t.id AS track_id,
                t.name AS track_name,
                t.artist_id AS artist_id,
                ar.name AS artist_name,
                t.album_id AS album_id,
                al.name AS album_name,
                al.release_date AS release_date,
                al.image_url AS image_url,
                af.video_id AS video_id,
                af.audio_path AS audio_path
            FROM tracks t
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums al ON t.album_id = al.id
            LEFT JOIN audio_files af ON t.id = af.track_id;
            """

            df = pd.read_sql_query(query, self.conn)
            output_csv = os.path.join(output_directory, "tracks_full.csv")
            df.to_csv(output_csv, index=False)
            return output_csv


        else:
            queries = {t: f"SELECT * from {t}" for t in ["tracks", "artists", "albums", "audio_files"]}
            output_csvs = []
            for t, q in queries.items():
                output_csv = os.path.join(output_directory, f"{t}.csv")
                pd.read_sql_query(q, self.conn).to_csv(output_csv, index=False)
                output_csvs.append(output_csv)
            return output_csvs
