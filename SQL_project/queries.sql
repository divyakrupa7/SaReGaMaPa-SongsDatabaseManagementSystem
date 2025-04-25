
-- Add a new user
INSERT INTO users (username, password, email, first_name, last_name)
VALUES ('ab', 'incorrect_password', 'ab@gmail.com', 'a', 'b');

-- Add a new playlist for a user
INSERT INTO playlists (name) VALUES ('My Favorite Songs');

--  Add a playlist to a user
INSERT INTO user_playlists (user_id, playlist_id)
VALUES (
    (SELECT user_id FROM users WHERE username = 'ab'),
    (SELECT playlist_id FROM playlists WHERE name = 'My Favorite Songs')
);

-- Add a song to a user's playlist
INSERT INTO playlist_song (playlist_id, song_id)
VALUES (
    (SELECT playlist_id FROM user_playlists WHERE user_id = (SELECT user_id FROM users WHERE username = 'user1') AND playlist_id = (SELECT playlist_id FROM playlists WHERE name = 'My Favorite Songs')),
    (SELECT song_id FROM songs WHERE title = 'Song Title')
);

-- Query to delete a song from a user's playlist
-- Replace 'user1' with the target user's username and 'My Favorite Songs' with the playlist name
DELETE FROM playlist_song
WHERE playlist_id = (SELECT playlist_id FROM user_playlists WHERE user_id = (SELECT user_id FROM users WHERE username = 'user1') AND playlist_id = (SELECT playlist_id FROM playlists WHERE name = 'My Favorite Songs'))
  AND song_id = (SELECT song_id FROM songs WHERE title = 'Song Title');

-- Query to update song information
-- Replace 'Old Song Title' with the old song title and 'New Song Title' with the new song title
UPDATE songs
SET title = 'New Song Title'
WHERE song_id = (SELECT song_id FROM songs WHERE title = 'Old Song Title');

-- Query to retrieve all playlists of a user
SELECT playlists.name
FROM playlists
JOIN user_playlists ON playlists.playlist_id = user_playlists.playlist_id
JOIN users ON user_playlists.user_id = users.user_id
WHERE users.username = 'user1';

-- Query to retrieve all songs in a user's playlist
SELECT songs.title, artists.name AS artist
FROM songs
JOIN playlist_song ON songs.song_id = playlist_song.song_id
JOIN playlists ON playlist_song.playlist_id = playlists.playlist_id
JOIN artists ON songs.album_id = artists.artist_id
WHERE playlists.name = 'My Favorite Songs';

-- Query to add a new playlist
INSERT INTO playlists (name) 
VALUES ('New Playlist');

-- Query to add a song to a playlist (after a playlist is created)
INSERT INTO playlist_song (playlist_id, song_id)
VALUES (
    (SELECT playlist_id FROM playlists WHERE name = 'New Playlist'),
    (SELECT song_id FROM songs WHERE title = 'Song Title')
);

