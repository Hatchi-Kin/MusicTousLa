import os
import sqlite3
import unittest
from unittest.mock import patch
from bot.models import create_tables, insert_first_song
from bot.utils import (
    get_participant,
    get_participants_usernames,
    get_all_participants_count,
    add_participant_to_db,
    remove_participant_from_db,
    get_all_participants,
    get_recent_djs,
    save_song,
)

# python3 -m unittest bot/tests.py


class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        self.test_db = "test.db"

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_create_tables(self):
        create_tables(self.test_db)
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()

        # Check if the tables were created
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()

        self.assertIn(("songs",), tables)
        self.assertIn(("participants",), tables)
        self.assertIn(("currentdj",), tables)

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

    @patch("bot.models.DatabaseManager.fetchone", return_value=("user_id",))
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_get_participant(self, init_mock, fetchone_mock):
        result = get_participant(self.test_db, "user_id")
        self.assertEqual(result, ("user_id",))
        init_mock.assert_called_once_with(self.test_db)
        fetchone_mock.assert_called_once_with(
            "SELECT user_id FROM participants WHERE user_id = ?", ("user_id",)
        )

    @patch(
        "bot.models.DatabaseManager.fetchall",
        return_value=[("username1",), ("username2",)],
    )
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_get_participants_usernames(self, init_mock, fetchall_mock):
        result = get_participants_usernames(self.test_db)
        self.assertEqual(result, [("username1",), ("username2",)])
        init_mock.assert_called_once_with(self.test_db)
        fetchall_mock.assert_called_once_with("SELECT username FROM participants")

    @patch("bot.models.DatabaseManager.fetchone", return_value=(2,))
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_get_all_participants_count(self, init_mock, fetchone_mock):
        result = get_all_participants_count(self.test_db)
        self.assertEqual(result, 2)
        init_mock.assert_called_once_with(self.test_db)
        fetchone_mock.assert_called_once_with("SELECT COUNT(*) FROM participants")

    @patch("bot.models.DatabaseManager.execute")
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_add_participant_to_db(self, init_mock, execute_mock):
        add_participant_to_db(self.test_db, "user_id", "username")
        init_mock.assert_called_once_with(self.test_db)
        execute_mock.assert_called_once_with(
            "INSERT INTO participants (user_id, username) VALUES (?, ?)",
            ("user_id", "username"),
        )

    @patch("bot.models.DatabaseManager.execute")
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_remove_participant_from_db(self, init_mock, execute_mock):
        remove_participant_from_db(self.test_db, "user_id")
        init_mock.assert_called_once_with(self.test_db)
        execute_mock.assert_called_once_with(
            "DELETE FROM participants WHERE user_id = ?", ("user_id",)
        )

    @patch(
        "bot.models.DatabaseManager.fetchall",
        return_value=[("user_id1", "username1"), ("user_id2", "username2")],
    )
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_get_all_participants(self, init_mock, fetchall_mock):
        result = get_all_participants(self.test_db)
        self.assertEqual(result, [("user_id1", "username1"), ("user_id2", "username2")])
        init_mock.assert_called_once_with(self.test_db)
        fetchall_mock.assert_called_once_with(
            "SELECT user_id, username FROM participants"
        )

    @patch(
        "bot.models.DatabaseManager.fetchall",
        return_value=[("user_id1",), ("user_id2",)],
    )
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_get_recent_djs(self, init_mock, fetchall_mock):
        result = get_recent_djs(self.test_db)
        self.assertEqual(result, [("user_id1",), ("user_id2",)])
        init_mock.assert_called_once_with(self.test_db)
        fetchall_mock.assert_called_once_with(
            "SELECT DISTINCT user_id FROM songs ORDER BY id DESC LIMIT 5"
        )

    @patch("bot.models.DatabaseManager.execute")
    @patch("bot.models.DatabaseManager.__init__", return_value=None)
    def test_save_song(self, init_mock, execute_mock):
        save_song(self.test_db, "user_id", "song_link")
        init_mock.assert_called_once_with(self.test_db)
        execute_mock.assert_called_once_with(
            "INSERT INTO songs (user_id, link) VALUES (?, ?)", ("user_id", "song_link")
        )


if __name__ == "__main__":
    unittest.main()
