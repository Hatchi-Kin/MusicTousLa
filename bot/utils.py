# from bot.models import DatabaseManager


# def get_participant(DB_NAME, user_id):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchone("SELECT user_id FROM participants WHERE user_id = ?", (user_id,))


# def get_participants_usernames(DB_NAME):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchall("SELECT username FROM participants")


# def get_all_participants_count(DB_NAME):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchone("SELECT COUNT(*) FROM participants")[0]


# def add_participant_to_db(DB_NAME, user_id, username):
#     db = DatabaseManager(DB_NAME)
#     db.execute(
#         "INSERT INTO participants (user_id, username) VALUES (?, ?)",
#         (user_id, f"{username}"),
#     )


# def remove_participant_from_db(DB_NAME, user_id):
#     db = DatabaseManager(DB_NAME)
#     db.execute("DELETE FROM participants WHERE user_id = ?", (user_id,))


# def get_all_participants(DB_NAME):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchall("SELECT user_id, username FROM participants")


# def get_recent_djs(DB_NAME):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchall("SELECT DISTINCT user_id FROM songs ORDER BY id DESC LIMIT 5")


# def set_current_dj(DB_NAME, user_id):
#     db = DatabaseManager(DB_NAME)
#     db.execute("DELETE FROM currentdj")
#     db.execute("INSERT INTO currentdj (user_id) VALUES (?)", (user_id,))


# def get_current_dj(DB_NAME):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchone("SELECT user_id FROM currentdj ORDER BY id DESC LIMIT 1")


# def save_song(DB_NAME, user_id, song_link):
#     db = DatabaseManager(DB_NAME)
#     db.execute("INSERT INTO songs (user_id, link) VALUES (?, ?)", (user_id, song_link))


# def get_all_songs(DB_NAME):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchall("SELECT link, user_id FROM songs ORDER BY id DESC")


# def get_last_song(DB_NAME):
#     db = DatabaseManager(DB_NAME)
#     return db.fetchone("SELECT link, user_id FROM songs ORDER BY id DESC LIMIT 1")


# def is_not_direct_message(message):
#     return message["channel_type"] != "im"


