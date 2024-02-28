import os
from dotenv import load_dotenv


def get_slack_app_token():
    load_dotenv()
    return os.environ["SLACK_APP_TOKEN"]


def get_slack_bot_token():
    load_dotenv()
    return os.environ["SLACK_BOT_TOKEN"]


def is_not_direct_message(message):
    return message["channel_type"] != "im"


def get_username_directly_from_slack(app, user_id):
    response = app.client.users_info(user=user_id)
    if response["ok"]:
        return response["user"]["name"]
    else:
        return None
