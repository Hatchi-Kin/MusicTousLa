
import re
import random

from bot.utils import is_not_direct_message, get_username_directly_from_slack
from . import app, db, logger


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
    - `last`: permet de voir les 5 derniers morceaux choisis par les précedents DJs\n
    - `participants`: permet de voir la liste des participants\n
    - `forceadd/<user_id>`: permet d'ajouter un participant à la liste des participants\n
    - `forceremove/<user_id>`: permet de retirer un participant de la liste des participants\n
    - `help`: Pour afficher ce message\n
    """

    say(text=help_message, channel=dm_channel)


@app.message(re.compile(r"^addme$"))
def add_participant(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]
    username = get_username_directly_from_slack(user_id)
    existing_user = db.get_participant_username_from_id(user_id)

    if existing_user:
        say(
            text=f"""<@{user_id}> est déjà dans la liste des participants""",
            channel=dm_channel,
        )
    else:
        db.add_participant_to_db(user_id, username)
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
    existing_user = db.get_participant_username_from_id(user_id)

    if existing_user:
        db.remove_participant_from_db(user_id)
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
    all_participants = db.get_all_participants()
    recent_djs = db.get_recent_djs()

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
    db.set_current_dj(random_dj[0])

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
    current_dj = db.get_current_dj()

    if not current_dj:
        say(
            text=f"hey <@{user_id}>, aucun DJ n'a été choisi pour le moment",
            channel=dm_channel,
        )
        return

    say(
        text=f"hey <@{user_id}>, le DJ de cette semaine est <@{current_dj[0]}>",
        channel=dm_channel,
    )


app.message(re.compile(r"^nextsong/"))
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

    current_dj = db.get_current_dj()

    if message["user"] != current_dj[0]:
        warning = f"\nAu fait,  <@{message['user']}>, tu n'es pas le DJ de la semaine. Normalement, c'est à <@{current_dj[0]}> de choisir le morceau de la semaine."
    else:
        warning = ""

    try:
        db.save_song(message["user"], song_link)
        say(
            text=f"""hey <@{message["user"]}>, ton morceau a été enregistré:\n{song_link}"""
            + warning,
            channel=message["channel"],
        )
    except Exception as e:
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
    last_song = db.get_last_song()

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
    all_songs = db.get_all_songs()

    # Filter out duplicates
    seen_links = set()
    last_songs = []
    for song in all_songs:
        if song[0] not in seen_links:
            seen_links.add(song[0])
            last_songs.append(song)
        if len(last_songs) == 5:
            break

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
        text=f"hey <@{user_id}>, voiçi les 5 derniers morceaux choisi:\n{songs_text}",
        channel=dm_channel,
    )


@app.message(re.compile(r"^participants$"))
def show_participants(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["user"]
    participants = db.get_every_participants_usernames()
    count = db.get_all_participants_count()

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


@app.message(re.compile(r"^forceadd/(\w+)$"))
def force_add_participant(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["text"].replace("forceadd/", "")
    username = get_username_directly_from_slack(user_id)
    existing_user = db.get_participant_username_from_id(user_id)

    if existing_user:
        say(
            text=f"""<@{user_id}> est déjà dans la liste des participants""",
            channel=dm_channel,
        )
    else:
        db.add_participant_to_db(user_id, username)
        say(
            text=f"""<@{user_id}> a bien été ajouté à la liste des participants""",
            channel=dm_channel,
        )


@app.message(re.compile(r"^forceremove/(\w+)$"))
def force_remove_participant(message, say):
    if is_not_direct_message(message):
        return

    dm_channel = message["channel"]
    user_id = message["text"].replace("forceremove/", "")
    existing_user = db.get_participant_username_from_id(user_id)

    if existing_user:
        db.remove_participant_from_db(user_id)
        say(
            text=f"""<@{user_id}> a bien été retiré de la liste des participants""",
            channel=dm_channel,
        )
    else:
        say(
            text=f"""<@{user_id}> n'est déjà pas dans la liste des participants""",
            channel=dm_channel,
        )
