import unittest
import os
from bot.models import DatabaseManager, insert_first_song


class TestDatabaseManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = "test.db"
        cls.db = DatabaseManager(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.db_path)

    def setUp(self):
        # This method will be called before each test method is run.
        self.db.execute("DELETE FROM participants")
        self.db.execute("DELETE FROM songs")

    def test_add_and_remove_participant(self):
        user_id = "test_user"
        username = "Test User"
        self.db.add_participant_to_db(user_id, username)
        result = self.db.get_participant_username_from_id(user_id)
        self.assertEqual(result[0], username)
        self.db.remove_participant_from_db(user_id)
        result = self.db.get_participant_username_from_id(user_id)
        self.assertIsNone(result)

    def test_set_and_get_current_dj(self):
        user_id = "test_user"
        self.db.add_participant_to_db(user_id, "Test User")
        result = self.db.get_current_dj()
        self.assertIsNone(result)
        self.db.set_current_dj(user_id)
        result = self.db.get_current_dj()
        self.assertEqual(result, user_id)

    def test_save_and_get_song(self):
        user_id = "test_user"
        song_link = "https://www.youtube.com/watch?v=test"
        self.db.save_song(user_id, song_link)
        result = self.db.get_last_song()
        self.assertEqual(result[0], song_link)
        self.assertEqual(result[1], user_id)
        user_id2 = "test_user2"
        song_link2 = "https://www.youtube.com/watch?v=test2"
        self.db.save_song(user_id2, song_link2)
        result = self.db.get_last_song()
        self.assertEqual(result[0], song_link2)


    def test_insert_first_song(self):
        insert_first_song(self.db_path)
        result = self.db.get_last_song()
        self.assertEqual(result[0], "<https://www.youtube.com/watch?v=9fygHXi85T4>")
        self.assertEqual(result[1], "U06KDAJF1KL")

    def test_get_all_songs(self):
        user_id = "test_user"
        song_link = "https://www.youtube.com/watch?v=test"
        self.db.save_song(user_id, song_link)
        result = self.db.get_all_songs()
        self.assertEqual(result[0][0], song_link)

    def test_get_all_participants(self):
        # Add 10 participants and store their usernames
        usernames = []
        for i in range(1, 11):
            user_id = f"test_user{i}"
            username = f"Test User{i}"
            usernames.append(username)
            self.db.add_participant_to_db(user_id, username)
        all_participants = self.db.get_all_participants()
        self.assertEqual(len(all_participants), len(usernames))
        # Check if all usernames are in the result
        all_usernames = [
            username[0] for username in self.db.get_every_participants_usernames()
        ]
        for username in usernames:
            self.assertIn(username, all_usernames)

    def test_get_recent_djs(self):
        # Add 10 songs from 10 different participants
        for i in range(1, 11):
            user_id = f"test_user{i}"
            song_link = f"https://www.youtube.com/watch?v=test{i}"
            self.db.save_song(user_id, song_link)
        recent_djs = self.db.get_recent_djs()
        self.assertEqual(len(recent_djs), 5)
        # Check if last 5 participants are in the result
        all_user_ids = [user_id[0] for user_id in self.db.get_all_participants()]
        for user_id in all_user_ids[-5:]:
            self.assertIn(user_id, recent_djs)

    def test_get_all_participants_count(self):
        result = self.db.get_all_participants_count()
        self.assertEqual(result, 0)
        for i in range(1, 4):
            user_id = f"test_user{i}"
            username = f"Test User{i}"
            self.db.add_participant_to_db(user_id, username)
        participant_count = self.db.get_all_participants_count()
        self.assertEqual(participant_count, 3)

    def test_get_every_participants_usernames(self):
        usernames = []
        for i in range(1, 5):
            user_id = f"test_user{i}"
            username = f"Test User{i}"
            usernames.append(username)
            self.db.add_participant_to_db(user_id, username)
        result = self.db.get_every_participants_usernames()
        result_usernames = [row[0] for row in result]
        self.assertCountEqual(usernames, result_usernames)
        self.assertEqual(self.db.get_all_participants_count(), len(usernames))


if __name__ == "__main__":
    unittest.main()
