
-- Table for users
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT,
    first_name TEXT,
    last_name TEXT,
    dob DATE,
    gender TEXT
);

-- Table for artists
CREATE TABLE artists (
    artist_id INT PRIMARY KEY,
    name TEXT
);

-- Table for albums
CREATE TABLE albums (
    album_id INT PRIMARY KEY,
    title TEXT,
    release_year INT,
    artist_id INT,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);

-- Table for songs
CREATE TABLE songs (
    song_id INT PRIMARY KEY,
    title TEXT,
    duration_seconds INT,
    album_id INT,
    genre TEXT,
    FOREIGN KEY (album_id) REFERENCES albums(album_id)
);

-- Table for playlists
CREATE TABLE playlists (
    playlist_id INT PRIMARY KEY,
    name TEXT UNIQUE
);

-- Table for playlist_song relationship
CREATE TABLE playlist_song (
    playlist_id INT,
    song_id INT,
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id),
    FOREIGN KEY (song_id) REFERENCES songs(song_id)
);



-- Table for user_playlists
CREATE TABLE user_playlists (
    user_id INT,
    playlist_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id)
);

-- Table for liked_songs
CREATE TABLE liked_songs (
    user_id INTEGER,
    song_id INTEGER,
    PRIMARY KEY (user_id, song_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (song_id) REFERENCES songs(song_id)
);

-- Table for following_artists
CREATE TABLE following_artists (
    user_id INTEGER,
    artist_id INTEGER,
    PRIMARY KEY (user_id, artist_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);




-- Create a view to get a list of songs and their associated artists and albums
CREATE VIEW song_details AS
SELECT
    songs.title AS song_title,
    artists.name AS artist_name,
    albums.title AS album_title
FROM songs
JOIN albums ON songs.album_id = albums.album_id
JOIN artists ON albums.artist_id = artists.artist_id;


-- Index on the artist_id column in albums table
CREATE INDEX idx_artist_id ON albums (artist_id);

-- Index on the album_id column in songs table
CREATE INDEX idx_album_id ON songs (album_id);

-- Index on the user_id column in user_playlists table
CREATE INDEX idx_user_id ON user_playlists (user_id);

-- Index on the playlist_id column in user_playlists table
CREATE INDEX idx_playlist_id ON user_playlists (playlist_id);
