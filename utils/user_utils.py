from datetime import datetime
from utils.utils import get_session
from shutil import copyfile
from utils import rss, utils

import json
import time


def status(username, status):
    return utils.repeat(
        event="update table",
        data={
            "filename": "accounts",
            "folder": "server",
            "table": "accounts",
            "set_values": f"status=\"{status}\", seen=\"{time.ctime()}\"",
            "where": f"username=\"{username}\""
        },
        return_type=bool
    )


def get_online():
    returned = utils.repeat(
        event="retrieve table",
        data={
            "filename": "server_info",
            "folder": ".",
            "table": "online",
            "select": "*",
            "where": ""
        },
        return_type=list
    )

    return len(returned)


def online(num, room_id, silent=False, testing=False):
    # TODO Server message
    if not testing:
        session = get_session()
    else:
        session = {"username": "Jush"}

    event = ""
    data = {}

    if num == 1:
        event = "append table"

        data = {
            "filename": "server_info",
            "folder": ".",
            "table": "online",
            "columns": "username",
            "values": f"\"{session['username']}\"",
            "unique": True
        }
    elif num == -1:
        event = "delete row"

        data = {
            "filename": "server_info",
            "folder": ".",
            "table": "online",
            "where": f"username=\"{session['username']}\"",
        }

    returned = utils.repeat(
        event=event,
        data=data,
        return_type=bool
    )

    return returned


def clear_online():
    return utils.repeat(
        event="truncate",
        return_type=bool,
        data={
            "filename": "server_info",
            "folder": ".",
            "table": "online"
        }
    )


def get_account_info(username):
    return utils.repeat(
        event="retrieve table",
        return_type=list,
        data={
            "filename": "accounts",
            "folder": "server",
            "table": "accounts",
            "select": "username, ip, status, seen, id, \"server role\"",
            "where": f"username=\"{username}\""
        }
    )[0]


def convert_to_datetime(ctime):
    return datetime.strptime(ctime, "%c")


def monitor_activity(username):
    session = get_session()

    for _ in range(10):
        seen = get_account_info(username)[3]

        if (datetime.now().second - convert_to_datetime(seen).second) > 5:
            status(username, "Left")
            online(-1, session["room_id"])
        rss.rss_socket.sleep(1)
        time.sleep(1)
