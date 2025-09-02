# SaReGaMaPa: Songs Database Management System

## Dependencies

- Python 3.8+
- Streamlit
- pandas
- sqlite3

## Install dependencies with:

pip install streamlit pandas

## Getting Started

### 1. Clone the Repository

git clone https://github.com/divyakrupa7/SaReGaMaPa-SongsDatabaseManagementSystem.git
cd saregama-music-app

### 2. Set Up the Database

- Ensure your `schema.sql` file is present in the project directory.
- Create the SQLite database and tables:
   sqlite3 songs.db < schema.sql

### 3. Run the Application

streamlit run app.py

- The app will open in your default web browser.
- Log in with a username from the `users` table or register as new user.
