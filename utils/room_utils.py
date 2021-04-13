from utils import rss
from utils import utils

import os
import datetime

# Rooms Dir
rdir = os.path.abspath(__file__)+"/../../data/rooms/"


def list_rooms() -> list:
    files = []

    for file in os.listdir(rdir):
        if file.endswith(".db"):
            files.append(file)

    return files


def get_room_messages(room_id: str) -> dict:
    ret = utils.repeat(
        event="retrieve messages",
        return_type=dict,
        data={
            "room_id": room_id
        }
    )
    return ret


def get_room_info(room_id: str, table: str, select: str = "*", where: str = "") -> list:
    data = {
        "table": table,
        "room_id": room_id,
        "select": select,
        "where": where
    }

    room_info = utils.repeat(
        function=rss.rss_socket.emit,
        event="retrieve room info",
        data=data,
        return_type=list
    )

    return room_info


def set_room_info(room_id: str, table: str, where: str, value: str) -> bool:
    data = {
        "filename": room_id,
        "folder": "rooms",
        "table": table,
        "set_values": value,
        "where": where
    }

    success = utils.repeat(
        event="update table",
        data=data,
        return_type=bool
    )
    return success


def get_room_name(room_id: str) -> str:
    ret = get_room_info(room_id=str(room_id), table="Name", select="Name")
    return ret[0][0]


def get_rooms() -> list:
    ret = utils.repeat(
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
