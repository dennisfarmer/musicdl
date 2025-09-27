from sqlite3 import connect, Connection, Cursor
from copy import deepcopy as copy
import os

import pandas as pd

from .containers import Track, Playlist, Album, Artist, TrackContainer, format_for_zip
from .config import config



class MusicDB:
    def __init__(self, music_db=None):
        if music_db is None:
            self.music_db = config["music_db"]
        else:
            self.music_db = music_db
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
        self.conn.commit()

    def _insert_collection(self, c: Album|Playlist):
        for track in c.tracks.values():
            print(track)
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
            self.music_db = musicdb
        basedir = os.path.dirname(os.path.abspath(self.music_db))
        os.makedirs(basedir, exist_ok=True)
        self.conn = connect(self.music_db)
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
        # todo: also delete wav files and track info csv
        if os.path.exists(self.music_db):
            os.remove(self.music_db)
        self.connect_to_database()

    def close(self):
        self.conn.close()

    def to_csv(self) -> str|list[str]:
        csv_storage = config["datadir"]
        #single_file = config["single_file"]
        #col_names = ["tracks", "artists", "albums", "audio_files"]
        #for file in os.listdir(csv_storage):
        #for col in col_names:
            #file = os.path.join(csv_storage, f"{col}.csv")
            #if os.path.exists(file): os.remove(file)
        output_csv = os.path.join(csv_storage, "tracks.csv")
        if os.path.exists(output_csv):
            os.remove(output_csv)
        query = """
        SELECT
            t.id AS track_id,
            t.name AS track_name,
            t.artist_id AS artist_id,
            ar.name AS artist_name,
            t.album_id AS album_id,
            al.name AS album_name,
            al.release_date AS release_date,
            al.artwork_url AS artwork_url,
            af.video_id AS youtube_url,
            af.audio_path AS audio_path
        FROM tracks t
        LEFT JOIN artists ar ON t.artist_id = ar.id
        LEFT JOIN albums al ON t.album_id = al.id
        LEFT JOIN audio_files af ON t.id = af.track_id;
        """

        df = pd.read_sql_query(query, self.conn)
        df["audio_path"] = df["audio_path"].apply(format_for_zip)

        # use full url for simplicity during later processing
        df["youtube_url"] = df["youtube_url"].apply(lambda v_id: f"https://www.youtube.com/watch?v={v_id}")

        df.to_csv(output_csv, index=False)
        return output_csv


        #else:
            #queries = {t: f"SELECT * from {t}" for t in col_names}
            #output_csvs = []
            #for t, q in queries.items():
                #output_csv = os.path.join(csv_storage, f"{t}_table.csv")
                #pd.read_sql_query(q, self.conn).to_csv(output_csv, index=False)
                #output_csvs.append(output_csv)
            #return output_csvs
    
    def update_from_csv(self, csv="./tracks/tracks.csv"):
        """
        loads tracks folder from given csv

        note: audio_path needs to be updated, I don't use this function
              but if I do make sure to fix (likely need to move files)
        """
        col_names = [
            "track_id", "track_name", "artist_id", "artist_name",
            "album_id", "album_name", "release_date", "image_url",
            "video_id", "audio_path"
        ]
        df = pd.read_csv(csv, names=col_names, header=0)
        for _, row in df.iterrows():
            track = Track(
                track_id=row["track_id"],
                name=row["track_name"],
                artist_id=row["artist_id"],
                artist_name=row["artist_name"],
                album_id=row["album_id"],
                album_name=row["album_name"],
                image_url=row["image_url"],
                release_date=row["release_date"],
                video_id=row["video_id"],
                audio_path=row["audio_path"]
            )


            self._insert_track(track)