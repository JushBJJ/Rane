from utils.room_utils import list_rooms
from utils.utils import get_ip, get_session
from flask import current_app as app
from flask.testing import FlaskClient
from utils import rss, utils

import json
import datetime
import flask


def autocolor(testing=False):
    session = get_session()

    if testing:
        session = {"username": "Jush"}

    data = {
        "table": "admins",
        "filename": "admins",
        "directory": "server"
    }

    admins = []

    admins = utils.repeat(
        event="select all",
        data=data,
        return_type=list)

    username = session["username"]

    for admin in admins:
        if username in admin[0]:
            username += "(<span class=\'admin\'>ADMIN</span>)"
            break

    session["special"] = username
    return session["special"]
