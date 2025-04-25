import streamlit as st
import sqlite3
import pandas as pd

db_path = "songs.db"  
conn = sqlite3.connect(db_path, check_same_thread=False)

# Helper function to get user ID from username
def get_user_id(username):
    query = f"SELECT user_id FROM users WHERE username = ?"
    result = conn.execute(query, (username,)).fetchone()
    return result[0] if result else None

# Helper function to register a new user
def register_user(username, password, email, first_name, last_name, dob, gender):
    query = "SELECT user_id FROM users WHERE username = ?"
    existing_user = conn.execute(query, (username,)).fetchone()
    
    if existing_user:
        st.error(f"Username '{username}' is already taken. Please choose a different one.")
    else:
        # Inserting the new user into the 'users' table
        query = """
            INSERT INTO users (username, password, email, first_name, last_name, dob, gender)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        conn.execute(query, (username, password, email, first_name, last_name, str(dob), gender))
        conn.commit()
        st.success(f"Account for {username} created successfully!")

# Helper function to check user authentication
def authenticate_user(username, password):
    query = "SELECT user_id FROM users WHERE username = ? AND password = ?"
    result = conn.execute(query, (username, password)).fetchone()
    return result[0] if result else None

# Helper function to get the "Liked Songs" playlist ID
def get_liked_songs_playlist():
    query = "SELECT playlist_id FROM playlists WHERE name = 'Liked Songs'"
    result = conn.execute(query).fetchone()
    return result[0] if result else None

# Helper function to check if a playlist already exists
def is_playlist_exists(playlist_name):
    query = "SELECT playlist_id FROM playlists WHERE name = ?"
    result = conn.execute(query, (playlist_name,)).fetchone()
    return result is not None
    
st.title("🎵 SaReGaMaPa")


# Checks if the user is logged in
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# Displays the login form if the user is not logged in
if st.session_state['user_id'] is None:
    st.header("Login to your account")

    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Login button
    login_button = st.button("Login")

    # Handle login logic
    if login_button:
        # Authenticating the user
        user_id = authenticate_user(username, password)
        if user_id:
            st.session_state['user_id'] = user_id  # Stores the user ID in session state
            st.session_state['username'] = username  # Stores the username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password. Please try again.")

    # Registration form
    register = st.checkbox("New User? Register here")

    if register:
        st.subheader("Register a new account")

        # Registration fields
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_email = st.text_input("Email")
        new_first_name = st.text_input("First Name")
        new_last_name = st.text_input("Last Name")
        dob = st.date_input("Date of Birth")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        # Register button
        if st.button("Register"):
            # Register new user
            register_user(new_username, new_password, new_email, new_first_name, new_last_name, dob, gender)
            st.success(f"Account for {new_username} created successfully!")
    
# If the user is logged in, this will show their data
if st.session_state['user_id'] is not None:
    user_id = st.session_state['user_id']
    username = st.session_state['username']

    logout_button = st.button("Logout")

    # logout logic
    if logout_button:
        st.session_state['user_id'] = None  # Clears the user session
        st.session_state['username'] = None
        
        
        # Reset session state to clear any previous user data
        for key in list(st.session_state.keys()):
            if key.startswith('follow_') or key.startswith('heart_'):
                del st.session_state[key]
        
        st.success(f"You have logged out. Come back soon, {username}!")
        st.rerun()

    st.header("Your Personalized Content")

# list of songs
    st.header("Songs")
    
    search_term = st.text_input("Search Songs","")

    songs_query = """
        SELECT 
            s.song_id, 
            s.title AS song_title,
            ar.name AS artist_name,
            s.duration_seconds
        FROM songs s
        JOIN albums al ON s.album_id = al.album_id
        JOIN artists ar ON al.artist_id = ar.artist_id
    """
    # songs_df = pd.read_sql_query(songs_query, conn)
    if search_term:
        songs_query += " WHERE s.title LIKE ?"
        songs_df = pd.read_sql_query(songs_query, conn, params=(f"%{search_term}%",))
    else:
        songs_df = pd.read_sql_query(songs_query, conn)

    # Converts seconds to MM:SS format
    songs_df['duration'] = songs_df['duration_seconds'].apply(
        lambda x: f"{x//60:02d}:{x%60:02d}"
    )

    def toggle_like(user_id, song_id, song_title):
        #current heart state from session_state
        current_state = st.session_state.get(f'heart_{song_id}', False)
        
        # Toggles the heart state (like/unlike)
        if current_state:
            # Unlike logic
            conn.execute("DELETE FROM liked_songs WHERE user_id=? AND song_id=?", (user_id, song_id))
            st.session_state[f'heart_{song_id}'] = False  # Set heart to unliked (🤍)
        else:
            # Like logic
            conn.execute("INSERT OR IGNORE INTO liked_songs (user_id, song_id) VALUES (?, ?)", (user_id, song_id))
            st.session_state[f'heart_{song_id}'] = True  # Set heart to liked (❤)
    
        playlist_id = get_liked_songs_playlist()
        if not playlist_id:
            conn.execute("INSERT INTO playlists (name) VALUES ('Liked Songs')")
            playlist_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        if current_state:
            conn.execute("DELETE FROM playlist_song WHERE playlist_id=? AND song_id=?", (playlist_id, song_id))
        else:
            conn.execute("INSERT OR IGNORE INTO playlist_song (playlist_id, song_id) VALUES (?, ?)", (playlist_id, song_id))
        
        conn.commit()

    # Displays each song with heart icon (like/unlike)
    for index, row in songs_df.iterrows():
        song_id = row['song_id']
        song_title = row['song_title']
        artist_name = row['artist_name']
        duration = row['duration']
        
        col1, col2, col3, col4 = st.columns([0.35, 0.25, 0.2, 0.2])

        with col1:
            st.markdown(f"**{song_title}**")
        with col2:
            st.markdown(f"{artist_name}")
        with col3:
            st.markdown(f"{duration}")
        with col4:
            
            initial_state = st.session_state.get(
                f'heart_{song_id}',
                bool(conn.execute(
                    "SELECT 1 FROM liked_songs WHERE user_id=? AND song_id=?",
                    (user_id, song_id)
                ).fetchone())
            )
            
            # Display the heart icon (❤️ or 🤍) based on the current state
            heart_icon = "❤️" if initial_state else "🤍"
            
            # Toggles the like/unlike action when the button is clicked
            if st.button(heart_icon, key=f"heart_btn_{song_id}", on_click=toggle_like, args=(user_id, song_id, song_title)):
                pass

    # Playlist Management Section
    st.header("Your Playlists")

    #  Gets the user's playlists
    playlists_query = """
        SELECT p.playlist_id, p.name 
        FROM playlists p
        JOIN user_playlists up ON p.playlist_id = up.playlist_id
        WHERE up.user_id = ?
    """
    playlists = conn.execute(playlists_query, (user_id,)).fetchall()

    #  Displays each playlist with songs
    for playlist in playlists:
        playlist_id, playlist_name = playlist
        
        # Gets songs in this playlist
        songs_query = """
            SELECT 
                s.title AS song_title,
                ar.name AS artist_name,
                s.duration_seconds
            FROM playlist_song ps
            JOIN songs s ON ps.song_id = s.song_id
            JOIN albums al ON s.album_id = al.album_id
            JOIN artists ar ON al.artist_id = ar.artist_id
            WHERE ps.playlist_id = ?
        """
        playlist_songs = pd.read_sql_query(songs_query, conn, params=(playlist_id,))
        
        # Displays playlist section
        with st.expander(f"🎵 {playlist_name}"):
            if not playlist_songs.empty:
                # Convert seconds to MM:SS
                playlist_songs['duration'] = playlist_songs['duration_seconds'].apply(
                    lambda x: f"{x//60:02d}:{x%60:02d}"
                )
                
                # Displays as table
                st.dataframe(
                    playlist_songs[['song_title', 'artist_name', 'duration']]
                    .rename(columns={
                        'song_title': 'Song',
                        'artist_name': 'Artist',
                        'duration': 'Duration'
                    }),
                    hide_index=True
                )
            else:
                st.write("This playlist is empty")
                
            # Adds songs to playlist controls
            st.divider()
            st.subheader("Add Songs to Playlist")
            
            # Song selection
            available_songs = pd.read_sql_query("""
                SELECT s.song_id, s.title, ar.name AS artist 
                FROM songs s
                JOIN albums al ON s.album_id = al.album_id
                JOIN artists ar ON al.artist_id = ar.artist_id
            """, conn)
            
            selected_song = st.selectbox(
                "Choose a song to add",
                available_songs.apply(lambda x: f"{x['title']} - {x['artist']}", axis=1),
                key=f"add_song_{playlist_id}"
            )
            
            if st.button("Add to Playlist", key=f"add_btn_{playlist_id}"):
                song_id = available_songs.iloc[available_songs.index[selected_song]]['song_id']
                
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO playlist_song (playlist_id, song_id) VALUES (?, ?)",
                        (playlist_id, song_id)
                    )
                    conn.commit()
                    st.success("Song added to playlist!")
                    playlists = conn.execute(playlists_query, (user_id,)).fetchall()
                except sqlite3.Error as e:
                    st.error(f"Error adding song: {str(e)}")

    # Creates New Playlist Section  
    st.header("Create New Playlist")
    new_playlist_name = st.text_input("Enter playlist name")

    if st.button("Create Playlist"):
        if new_playlist_name:
            # Check if the playlist already exists
            if is_playlist_exists(new_playlist_name):
                st.error(f"Playlist '{new_playlist_name}' already exists. Please choose a different name.")
            else:
                try:
                # Creates new playlist
                    conn.execute(
                        "INSERT INTO playlists (name) VALUES (?)",
                        (new_playlist_name,)
                    )
                    new_playlist_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    
                    # Link to the user
                    conn.execute(
                        "INSERT INTO user_playlists (user_id, playlist_id) VALUES (?, ?)",
                        (user_id, new_playlist_id)
                    )
                    conn.commit()
                    st.success("Playlist created successfully!")
                    st.session_state['create_playlist_success'] = True
                    st.rerun()  
                except sqlite3.Error as e:
                    st.error(f"Error creating playlist: {str(e)}")
        else:
            st.warning("Please enter a playlist name")

    def toggle_follow(user_id, artist_id, artist_name):
        current_state = st.session_state[f'follow_{artist_id}']
        
        try:
            if current_state:
                # Remove from following_artists
                conn.execute("""
                    DELETE FROM following_artists 
                    WHERE user_id=? AND artist_id=?
                """, (user_id, artist_id))
            else:
                # Add to following_artists
                conn.execute("""
                    INSERT OR IGNORE INTO following_artists 
                    VALUES (?, ?)
                """, (user_id, artist_id))
            
            st.session_state[f'follow_{artist_id}'] = not current_state
            conn.commit()
            
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")


    st.header("Artists")
    artists = conn.execute("""
        SELECT a.artist_id, a.name, 
            EXISTS(SELECT 1 FROM following_artists 
                    WHERE user_id=? AND artist_id=a.artist_id) AS is_following
        FROM artists a
        ORDER BY a.name
    """, (user_id,)).fetchall()

    for artist in artists:
        artist_id = artist[0]
        artist_name = artist[1]
        is_following = artist[2]
        
        # Initializes session state
        if f'follow_{artist_id}' not in st.session_state:
            st.session_state[f'follow_{artist_id}'] = bool(is_following)
        
        col1, col2 = st.columns([0.8, 0.2])

        with col1:
            st.markdown(f"**{artist_name}**")

        with col2:
            btn_emoji = "✅" if st.session_state[f'follow_{artist_id}'] else "➕"
            if st.button(
                btn_emoji,
                key=f"follow_btn_{artist_id}",
                on_click=toggle_follow,
                args=(user_id, artist_id, artist_name)
            ):
                pass
                
        
        
        st.divider()



    st.header("Liked Songs")
    liked_songs_query = """
        SELECT 
            s.title AS song_title,
            ar.name AS artist_name,
            s.duration_seconds
        FROM liked_songs ls
        JOIN songs s ON ls.song_id = s.song_id
        JOIN albums al ON s.album_id = al.album_id
        JOIN artists ar ON al.artist_id = ar.artist_id
        WHERE ls.user_id = ?
    """
    liked_songs_df = pd.read_sql_query(liked_songs_query, conn, params=(user_id,))
    st.session_state[f"liked_songs_{user_id}"] = liked_songs_df  


    if not liked_songs_df.empty:
        display_df = liked_songs_df.copy()
        display_df['duration'] = display_df['duration_seconds'].apply(
            lambda x: f"{x//60:02d}:{x%60:02d}"
        )
        st.dataframe(
            display_df[['song_title', 'artist_name', 'duration']]
            .rename(columns={
                'song_title': 'Song',
                'artist_name': 'Artist',
                'duration': 'Duration'
            }),
            hide_index=True
        )
    else:
        st.write("You haven't liked any songs yet.")
        
    st.header("Popular Songs")

    popular_songs_query = """
    SELECT 
        s.title AS song_title,
        ar.name AS artist_name,
        COUNT(ls.user_id) AS likes
    FROM liked_songs ls
    JOIN songs s ON ls.song_id = s.song_id
    JOIN albums al ON s.album_id = al.album_id
    JOIN artists ar ON al.artist_id = ar.artist_id
    GROUP BY s.song_id
    ORDER BY likes DESC
    LIMIT 5;
    """

    popular_songs_df = pd.read_sql_query(popular_songs_query, conn)

    if not popular_songs_df.empty:
        formatted_df = popular_songs_df.copy()
        formatted_df.index = ['1', '2', '3', '4', '5'][:len(formatted_df)]
        
        st.dataframe(
            formatted_df[['song_title', 'artist_name', 'likes']]
            .rename(columns={
                'song_title': 'Song',
                'artist_name': 'Artist',
                'likes': 'Likes'
            }),
            use_container_width=True
        )
    else:
        st.write("No likes yet - be the first to like a song!")

    st.header("Artists You Follow")
    following_artists_query = f"""
        SELECT a.name 
        FROM following_artists fa
        JOIN artists a ON fa.artist_id = a.artist_id
        WHERE fa.user_id = {user_id};
    """
    following_artists_df = pd.read_sql_query(following_artists_query, conn)
    if not following_artists_df.empty:
        st.write(following_artists_df)
    else:
        st.write("You aren't following any artists yet.")