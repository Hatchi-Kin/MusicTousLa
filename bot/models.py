import sqlite3
import logging


def create_tables(self):
    try:
        with sqlite3.connect(self) as conn:
            c = conn.cursor()

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS songs(
                    id INTEGER PRIMARY KEY,
                    link TEXT NOT NULL,
                    user_id TEXT NOT NULL
                )
                """
            )
            
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS participants(
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL
                )
                """
            )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS currentdj(
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL
                )
                """
            )

    except sqlite3.Error as e:
        logging.error(f"An error occurred in create_tables: {e}")


def insert_first_song(self):
    try:
        with sqlite3.connect(self) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM songs")
            if not c.fetchone():
                c.execute(
                    """
                    INSERT INTO songs (link, user_id) VALUES (?, ?)
                    """,
                    ("<https://www.youtube.com/watch?v=9fygHXi85T4>", "U06KDAJF1KL"),
                )
    except sqlite3.Error as e:
        logging.error(f"An error occurred in insert_first_song: {e}")


class DatabaseManager:

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        create_tables(db_path)
        insert_first_song(db_path)

    def execute(self, query, params=()):
        with self.conn:
            self.conn.execute(query, params)

    def fetchone(self, query, params=()):
        with self.conn:
            return self.conn.execute(query, params).fetchone()

    def fetchall(self, query, params=()):
        with self.conn:
            return self.conn.execute(query, params).fetchall()

    def get_participant_username_from_id(self, user_id):
        return self.fetchone(
            "SELECT username FROM participants WHERE user_id = ?", (user_id,)
        )

    def get_every_participants_usernames(self):
        return self.fetchall("SELECT username FROM participants")

    def get_all_participants_count(self):
        return self.fetchone("SELECT COUNT(*) FROM participants")[0]

    def add_participant_to_db(self, user_id, username):
        self.execute(
            "INSERT INTO participants (user_id, username) VALUES (?, ?)",
            (user_id, f"{username}"),
        )

    def remove_participant_from_db(self, user_id):
        self.execute("DELETE FROM participants WHERE user_id = ?", (user_id,))

    def get_all_participants(self):
        return self.fetchall("SELECT user_id, username FROM participants")

    def get_recent_djs(self):
        return self.fetchall(
            "SELECT DISTINCT user_id FROM songs ORDER BY id DESC LIMIT 5"
        )

    def set_current_dj(self, user_id):
        self.execute("DELETE FROM currentdj")
        self.execute("INSERT INTO currentdj (user_id) VALUES (?)", (user_id,))

    def get_current_dj(self):
        return self.fetchone("SELECT user_id FROM currentdj ORDER BY id DESC LIMIT 1")

    def save_song(self, user_id, song_link):
        self.execute(
            "INSERT INTO songs (user_id, link) VALUES (?, ?)", (user_id, song_link)
        )

    def get_all_songs(self):
        return self.fetchall("SELECT link, user_id FROM songs ORDER BY id DESC")

    def get_last_song(self):
        return self.fetchone("SELECT link, user_id FROM songs ORDER BY id DESC LIMIT 1")
