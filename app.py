import logging
import os
import re
import sqlite3
import random

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


load_dotenv()

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

DB_NAME = "db/music_tous_la.db"


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
    def __init__(self):
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


def is_not_direct_message(message):
    return message["channel_type"] != "im"


def get_username(user_id):
    response = app.client.users_info(user=user_id)
    if response["ok"]:
        return response["user"]["name"]
    else:
        return None


app = App(token=SLACK_BOT_TOKEN, name="MusicTousLa")
logger = logging.getLogger(__name__)
create_tables(DB_NAME)
insert_first_song(DB_NAME)


@app.message(re.compile(r"^help$"))
def show_help(message, say):
    """Shows the help message"""
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    help_message = f"""hey <@{user_id}>, Pour intéragir avec le bot, il faut lui envoyer des commandes par mp.
    Les commandes disponibles sont:\n
    - `addme`: Pour s'ajouter à la liste des participants\n
    - `removeme`: Pour se retirer de la liste des participants\n
    - `randomdj`: Choisit au hasard le prochain DJ\n
    - `isdj`: permet de voir qui est le DJ de la semaine\n
    - `nextsong/<song_link>`: permet au DJ de la semaine d'enregistrer l'URL du morceau choisit (ex, un lien youtube)\n
    - `song`: permet de voir le morceau choisi par le DJ de la semaine\n
    - `last`: permet de voir les 3 derniers morceaux choisis par les précedents DJs\n
    - `participants`: permet de voir la liste des participants\n
    - `help`: Pour afficher ce message\n
    """

    say(text=help_message, channel=dm_channel)


@app.message(re.compile(r"^addme$"))
def add_participant(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]
    username = get_username(user_id)

    db = DatabaseManager()
    existing_user = db.fetchone(
        "SELECT user_id FROM participants WHERE user_id = ?", (user_id,)
    )

    if existing_user:
        say(
            text=f"""<@{user_id}> is already a participant""",
            channel=dm_channel,
        )
    else:
        db.execute(
            "INSERT INTO participants (user_id, username) VALUES (?, ?)",
            (user_id, f"{username}"),
        )

        say(
            text=f"""<@{user_id}> a été ajouté à la liste des participants""",
            channel=dm_channel,
        )


@app.message(re.compile(r"^removeme$"))
def remove_participant(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    db = DatabaseManager()
    existing_user = db.fetchone(
        "SELECT user_id FROM participants WHERE user_id = ?", (user_id,)
    )

    if existing_user:
        db.execute("DELETE FROM participants WHERE user_id = ?", (user_id,))
        say(
            text=f"""<@{user_id}> a été retiré de la liste des participants""",
            channel=dm_channel,
        )
    else:
        say(
            text=f"""<@{user_id}> n'est pas dans la liste des participants""",
            channel=dm_channel,
        )


@app.message(re.compile(r"^randomdj$"))
def random_dj(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    db = DatabaseManager()

    all_participants = db.fetchall("SELECT user_id, username FROM participants")
    recent_djs = db.fetchall(
        "SELECT DISTINCT user_id FROM songs ORDER BY id DESC LIMIT 5"
    )

    if len(recent_djs) < 5:
        available_djs = all_participants
    else:
        available_djs = [dj for dj in all_participants if dj not in recent_djs]

    if not available_djs:
        say(
            text=f"""There are no available DJs.""",
            channel=dm_channel,
        )
        return

    random_dj = random.choice(available_djs)

    # Remove the current DJ from the table then add the new one
    db.execute("DELETE FROM currentdj")
    db.execute("INSERT INTO currentdj (user_id) VALUES (?)", (random_dj[0],))

    # Send a message to the channel announcing the DJ for the next week
    say(
        text=f"""hey <@{user_id}>, le DJ de cette semaine est <@{random_dj[0]}>""",
        channel=dm_channel,
    )

    # And send a direct message to the selected DJ
    app.client.chat_postMessage(
        channel=random_dj[0],
        text=f"""Hey <@{random_dj[0]}>, tu as été choisi comme DJ de la semaine! Choisis un morceau et envoie le lien avec la commande `nextsong/<song_link>`""",
    )


@app.message(re.compile(r"^isdj$"))
def show_current_dj(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    db = DatabaseManager()
    current_dj = db.fetchone("SELECT user_id FROM currentdj ORDER BY id DESC LIMIT 1")

    if not current_dj:
        say(
            text=f"hey <@{user_id}>, aucun DJ n'a été choisi pour le moment",
            channel=dm_channel,
        )
        return

    say(
        text=f"hey <@{user_id}>, le DJ de cette semaine est <{current_dj[0]}>",
        channel=dm_channel,
    )


@app.message(re.compile(r"^nextsong/"))
def save_song_link(message, say):
    if is_not_direct_message(message):
        return

    song_link = message["text"].replace("nextsong/", "").strip()
    if song_link == "":
        say(
            text=f"""hey <@{message["user"]}>, tu n'as pas envoyé de lien de morceau. La commande est: `nextsong/<song_link>`""",
            channel=message["channel"],
        )
        return

    db = DatabaseManager()

    # Check if the user is the current DJ
    current_dj = db.fetchone("SELECT user_id FROM currentdj ORDER BY id DESC LIMIT 1")
    if message["user"] != current_dj[0]:
        warning = f"En fait,  <@{message['user']}>, tu n'es pas le DJ de la semaine. Normalement, c'est à <@{current_dj[0]}> de choisir le morceau de la semaine."
    else:
        warning = ""

    try:
        db.execute(
            "INSERT INTO songs (user_id, link) VALUES (?, ?)",
            (message["user"], song_link),
        )
        say(
            text=f"""hey <@{message["user"]}>, ton morceau a été enregistré:\n{song_link}"""
            + warning,
            channel=message["channel"],
        )
    except sqlite3.Error as e:
        logger.error(f"Failed to save song link: {e}")
        say(
            text=f"""hey <@{message["user"]}>, il y a eu une erreur en enregistrant ton morceau. Réessaye plus tard.""",
            channel=message["channel"],
        )


@app.message(re.compile(r"^song$"))
def show_song(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    db = DatabaseManager()
    last_song = db.fetchone("SELECT link, user_id FROM songs ORDER BY id DESC LIMIT 1")

    if not last_song:
        say(
            text=f"""hey <@{user_id}>, aucun morceau n'a été choisi pour le moment""",
            channel=dm_channel,
        )
        return

    say(
        text=f"""hey <@{user_id}>, cette semaine, <@{last_song[1]}> a choisit pour nous :\n{last_song[0]}""",
        channel=dm_channel,
    )


@app.message(re.compile(r"^last$"))
def show_last_songs(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    db = DatabaseManager()
    last_songs = db.fetchall(
        "SELECT link, user_id FROM songs ORDER BY id DESC LIMIT 5",
    )

    if not last_songs:
        say(
            text=f"hey <@{user_id}>, tu n'as pas encore choisi de morceau.",
            channel=dm_channel,
        )
        return

    songs_text = "\n".join(
        [f"{i+1}. {song[0]}, <@{song[1]}>" for i, song in enumerate(last_songs)]
    )
    say(
        text=f"hey <@{user_id}>, vois les 3 derniers morceaux choisi:\n{songs_text}",
        channel=dm_channel,
    )


@app.message(re.compile(r"^participants$"))
def show_participants(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    db = DatabaseManager()
    participants = db.fetchall("SELECT username FROM participants")
    count = db.fetchone("SELECT COUNT(*) FROM participants")[0]

    if not participants:
        say(
            text=f"""hey <@{user_id}>, il n'y a pas encore de participants""",
            channel=dm_channel,
        )
        return

    participants_list = "\n".join(
        [f"- <@{participant[0]}>" for participant in participants]
    )

    say(
        text=f"""hey <@{user_id}>, voici la liste des {count} participants:\n{participants_list}""",
        channel=dm_channel,
    )


# @app.message(re.compile(r"^usernameof/(\w+)$"))
# def get_username_of_user(message, say):
#     if is_not_direct_message(message):
#         return
#     user_id = message["text"].replace("usernameof/", "")
#     username = get_username(user_id)
#     say(
#         text=f"""L'username de {user_id} est <@{username}>""",
#         channel=message["channel"],
#     )


def main():
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
