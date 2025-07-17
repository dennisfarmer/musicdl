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
