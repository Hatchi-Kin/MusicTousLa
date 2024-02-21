import sqlite3
import logging


def create_tables(DB_NAME):
    try:
        with sqlite3.connect(DB_NAME) as conn:
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


def insert_first_song(DB_NAME):
    try:
        with sqlite3.connect(DB_NAME) as conn:
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
    def __init__(self, DB_NAME):
        self.db_name = DB_NAME
        self.conn = sqlite3.connect(self.db_name)

    def execute(self, query, params=()):
        with self.conn:
            self.conn.execute(query, params)

    def fetchone(self, query, params=()):
        with self.conn:
            return self.conn.execute(query, params).fetchone()

    def fetchall(self, query, params=()):
        with self.conn:
            return self.conn.execute(query, params).fetchall()
