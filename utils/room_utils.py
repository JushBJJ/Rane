from utils import rss
from utils import utils

import base64

import os

# Rooms Dir
rdir = os.path.abspath(__file__)+"/../../data/rooms/"


def list_rooms() -> list:
    """Get a list of rooms by database file."""
    files = []

    for file in os.listdir(rdir):
        if file.endswith(".db"):
            files.append(file)

    return files


def get_room_messages(room_id: str) -> tuple:
    """Get every message and media from a room."""
    ret = utils.call_db(
        event="retrieve messages",
        return_type=dict,
        data={
            "room_id": room_id
        }
    )
    return ret


def get_room_info(room_id: str, table: str, select: str = "*", where: str = "") -> list:
    """Get all info of selected room."""
    data = {
        "table": table,
        "room_id": room_id,
        "select": select,
        "where": where
    }

    room_info = utils.call_db(
        function=rss.rss_socket.emit,
        event="retrieve room info",
        data=data,
        return_type=list
    )

    return room_info


def set_room_info(room_id: str, table: str, where: str, value: str) -> bool:
    """Modify room values."""
    data = {
        "filename": room_id,
        "folder": "rooms",
        "table": table,
        "set_values": value,
        "where": where
    }

    success = utils.call_db(
        event="update table",
        data=data,
        return_type=bool
    )
    return success


def get_room_name(room_id: str) -> str:
    """Get room name."""
    ret = get_room_info(room_id=str(room_id), table="Name", select="Name")
    return ret[0][0]


def get_rooms() -> list:
    """Get a list of rooms register in the rooms database."""
    ret = utils.call_db(
        event="retrieve table",
        return_type=list,
        data={
            "filename": "rooms",
            "folder": ".",
            "table": "Rooms",
            "select": "*",
            "where": ""
        }
    )

    return ret


def get_user_rooms(username: str) -> list:
    """Get a list of rooms register in the rooms database."""
    ret = utils.call_db(
        event="retrieve table",
        return_type=list,
        data={
            "filename": "accounts",
            "folder": "server",
            "table": "accounts",
            "select": "rooms",
            "where": f"username=\"{username}\""
        }
    )[0][0]

    # Decode base64
    try:
        base64.b64decode(ret)
    except:
        pass

    return ret
