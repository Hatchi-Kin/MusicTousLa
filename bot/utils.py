from . import app


def is_not_direct_message(message):
    return message["channel_type"] != "im"


def get_username_directly_from_slack(user_id):
    response = app.client.users_info(user=user_id)
    if response["ok"]:
        return response["user"]["name"]
    else:
        return None