import logging
from bot.models import DatabaseManager
from bot.utils import get_slack_app_token, get_slack_bot_token
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


DB_NAME = "db/music_tous_la.db"

app = App(token=get_slack_bot_token(), name="MusicTousLa")
logger = logging.getLogger(__name__)
db = DatabaseManager(DB_NAME)
handler = SocketModeHandler(app, get_slack_app_token())

from . import listeners
