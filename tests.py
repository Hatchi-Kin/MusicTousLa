import os
import sqlite3
import unittest
from unittest.mock import patch
from app import create_tables, insert_first_song

# python3 -m unittest tests.py

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        self.test_db = "test.db"
        self.env_vars = {
            'SLACK_APP_TOKEN': 'test_token',
            'SLACK_BOT_TOKEN': 'test_token'
        }
        self.patcher = patch.dict(os.environ, self.env_vars)
        self.patcher.start()

    def tearDown(self):
        os.remove(self.test_db)

    def test_create_tables(self):
        create_tables(self.test_db)
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()

        # Check if the tables were created
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()

        self.assertIn(('songs',), tables)
        self.assertIn(('participants',), tables)
        self.assertIn(('currentdj',), tables)

    def test_insert_first_song(self):
        create_tables(self.test_db)
        insert_first_song(self.test_db)
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()

        # Check if the first song was inserted
        c.execute("SELECT * FROM songs")
        song = c.fetchone()

        self.assertIsNotNone(song)
        self.assertEqual(song[1], "<https://www.youtube.com/watch?v=9fygHXi85T4>")
        self.assertEqual(song[2], "U06KDAJF1KL")

if __name__ == '__main__':
    unittest.main()