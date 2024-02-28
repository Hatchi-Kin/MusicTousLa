import logging
import os

from bot.models import DatabaseManager
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


load_dotenv()

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

DB_NAME = "db/music_tous_la.db"

app = App(token=SLACK_BOT_TOKEN, name="MusicTousLa")
logger = logging.getLogger(__name__)
db = DatabaseManager(DB_NAME)
handler = SocketModeHandler(app, SLACK_APP_TOKEN)

from . import listeners  