import unittest
import os
from bot.models import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = 'test.db'
        cls.db = DatabaseManager(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.db_path)

    def test_add_and_remove_participant(self):
        user_id = 'test_user'
        username = 'Test User'
        self.db.add_participant_to_db(user_id, username)
        result = self.db.get_participant_username_from_id(user_id)
        self.assertEqual(result[0], username)
        self.db.remove_participant_from_db(user_id)
        result = self.db.get_participant_username_from_id(user_id)
        self.assertIsNone(result)

    def test_save_and_get_song(self):
        user_id = 'test_user'
        song_link = 'https://www.youtube.com/watch?v=test'
        self.db.save_song(user_id, song_link)
        result = self.db.get_last_song()
        self.assertEqual(result, (song_link, user_id))


# test if 


if __name__ == '__main__':
    unittest.main()