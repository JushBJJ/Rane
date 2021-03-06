from utils import rss, utils
from datetime import datetime
from utils.utils import get_session

import json
import time


def status(username: str, status: str) -> bool:
    """Set the status of a user, including when they were last seen."""

    if status == "Left":
        # TODO: Remove from online table
        utils.call_db(
            event="delete row",
            data={
                "filename": "server_info",
                "folder": ".",
                "table": "online",
                "where": f"username={username}"
            },
            return_type=bool
        )

    return utils.call_db(
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

    check_online()

    returned = utils.call_db(
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

    returned = utils.call_db(
        event=event,
        data=data,
        return_type=bool
    )

    return returned


def clear_online() -> bool:
    """Truncate online users table."""
    return utils.call_db(
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
    return utils.call_db(
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

    role = dict(utils.call_db(
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

    role = dict(utils.call_db(
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


def check_online():
    """Check if all users in server_info in table online are last seen 2 minutes ago"""
    session = get_session()
    online_users = utils.call_db(
        event="retrieve table",
        data={
            "filename": "server_info",
            "folder": ".",
            "table": "online",
            "select": "username",
            "where": ""
        },
        return_type=list
    )

    accounts = utils.call_db(
        event="retrieve table",
        data={
            "filename": "accounts",
            "folder": "server",
            "table": "accounts",
            "select": "username",
            "where": ""
        },
        return_type=list
    )

    accounts = list(map(lambda x: x[0], accounts))

    # Remove user if they don't exist
    for user in online_users:
        if user[0] not in accounts:
            # Remove from database
            utils.call_db(
                event="delete row",
                data={
                    "filename": "server_info",
                    "folder": ".",
                    "table": "online",
                    "where": f"username=\"{user[0]}\""
                },
                return_type=bool
            )

        else:
            # Check if they're online for the last 2 minutes, at the same date and hour
            # Example of get_account_info output: ('Jush', '192.168.1.15', 'Joined', 'Fri Oct 22 09:26:07 2021', 1, None)
            info = get_account_info(user[0])

            time_now = datetime.now()
            user_seen = convert_to_datetime(info[3])
            check = ["year", "month", "day", "hour", "minute"]

            for i in check:
                if i == "minute":
                    if (time_now.minute - user_seen.minute) > 2:
                        status(user[0], "Left")
                        break
                elif getattr(time_now, i) != getattr(user_seen, i):
                    status(user[0], "Left")
                    break


def get_user_rooms(username: str) -> list:
    """Get a user's rooms."""
    rooms = utils.call_db(
        event="retrieve table",
        data={
            "filename": "accounts",
            "folder": "server",
            "table": "accounts",
            "select": "rooms",
            "where": f"Username=\"{username}\""
        },
        return_type=str
    )[0][0]

    rooms = json.loads(rooms)["rooms"]
    return rooms
