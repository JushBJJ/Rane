from utils import rss, utils
from datetime import datetime
from utils.utils import get_session

import json
import time


def status(username: str, status: str) -> bool:
    """Set the status of a user, including when they were last seen."""
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


def get_online() -> int:
    """Get the amount of users that are online."""
    # TODO Get usernames that are online
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


def online(num: int, room_id: int, silent: bool = False, testing: bool = False) -> bool:
    """Set the value of whether the user is connected to the server or not."""
    # TODO Server message
    if not testing:
        session = get_session()
    else:
        session = {"username": "Jush"}

    event = ""
    data = {}

    # Set to Online
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

    # Set to Offline
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


def clear_online() -> bool:
    """Truncate online users table."""
    return utils.repeat(
        event="truncate",
        return_type=bool,
        data={
            "filename": "server_info",
            "folder": ".",
            "table": "online"
        }
    )


def get_account_info(username: str) -> list:
    """Get a user's info excluding their password."""
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


def get_account_server_role(username: str) -> str:
    """Get the user's server role."""
    data = {
        "table": "accounts",
        "filename": "accounts",
        "folder": "server",
        "select": "username, \"server role\"",
        "where": f"username=\"{username}\""
    }

    role = dict(utils.repeat(
        event="retrieve table",
        data=data,
        return_type=list
    ))

    if username in role.keys():
        if role[username] == None:
            return ""
        return role[username]

    return ""


def get_account_room_role(username: str, room_id: str) -> str:
    """Get the user's assigned room role."""

    if type(room_id) != str:
        raise TypeError("Invalid type: "+str(room_id))

    data = {
        "table": "Members",
        "filename": room_id,
        "folder": "rooms",
        "select": "Username, Role",
        "where": f"username=\"{username}\""
    }

    role = dict(utils.repeat(
        event="retrieve table",
        data=data,
        return_type=list
    ))

    if username in role.keys():
        return role[username]

    return "Member"


def convert_to_datetime(ctime: str) -> datetime:
    """Convert ctime to datetime."""
    return datetime.strptime(ctime, "%c")


def monitor_activity(username: str) -> None:
    """Monitor whether the user disconnected for more than 5 seconds, then determine whether they're offline or not."""
    session = get_session()

    for _ in range(10):
        seen = get_account_info(username)[3]

        if (datetime.now().second - convert_to_datetime(seen).second) > 5:
            status(username, "Left")
            online(-1, session["room_id"])
        rss.rss_socket.sleep(1)
        time.sleep(1)
