from flask import session, request
from datetime import datetime
from socketio.exceptions import ConnectionRefusedError
from routes.create_routes import create_routes
from client import website_connection as wc

import requests
from utils import room_utils, user_utils, chat_utils, rss, utils
from routes.auth import auth

import create_app

import time
import base64
import os
import hashlib
import html
import secrets
import atexit


create_app.create("config.py")

app = create_app.app
api = create_app.api
client_socket = create_app.socketio
HOST = app.config["HOST"]
PORT = app.config["PORT"]

api.add_resource(auth.authorize, "/api/authorize")


def register_external_receivers() -> None:
    client_socket.on_event("disconnect", wc.client_disconnected)
    client_socket.on_event("connect", wc.client_connect)
    client_socket.on_event("connected", wc.connected)
    client_socket.on_event("rss maintenance", wc.client_maintenance)

# Client-side
# Rooms Functions


@ client_socket.on("create_room")
def createRoom(args: dict) -> bool:
    name: str = html.escape(args["name"])
    desc: str = html.escape(args["desc"])
    public = int(args["public"] == "Public")
    owner = args["owner"]

    owner_id = user_utils.get_account_info(owner)[4]
    new_room_id = base64.b64encode(str(secrets.randbits(128)).encode()).decode()

    ret = utils.repeat(
        event="append table",
        return_type=bool,
        data={
            "filename": "rooms",
            "folder": ".",
            "table": "Rooms",
            "columns": "Name, Description, ID, Public",
            "values": f"\"{name}\", \"{desc}\", \"{new_room_id}\", \"{public}\"",
            "unique": False
        }
    )

    returns = utils.repeat(
        event="create room",
        return_type=list,
        data={
            "name": name,
            "owner": owner,
            "owner_id": owner_id,
            "room_id": new_room_id
        }
    )

    return ret and all(r == True for r in returns)


@client_socket.on("get_rooms")
def get_rooms(data: dict) -> None:
    pong = data["pong"]

    rooms = room_utils.get_rooms()
    section = ""

    for room in rooms:
        section += f"""
        <div class = \"chatroom-side\" >
            <a class=\"room-link\" onclick=\'move_room(\"{room[2]}\",\"{room[0]}\")\'>
                <p class = \"chatroom-title\" > {room[0]} </p> <i> 
                <p class = \"chatroom-description\">{room[1]}</p></i>
            </a>
        </div>"""

    client_socket.emit("recieve_rooms", {"rooms": section})
    client_socket.emit(pong)

# Messages


@client_socket.on("new comment")
def get_new_comment(data: dict) -> None:
    room_id = data["room_id"]
    message = data["message"]

    client_socket.emit("recieve_local_message", data)


@client_socket.on("get_comments")
def get_comments(data: dict) -> None:
    room_id = data["params"]
    pong = data["pong"]

    messages = room_utils.get_room_messages(room_id)
    newMessages = ""

    for message in messages["messages"]:
        newMessages += utils.convert_to_html(message)

    client_socket.emit("recieve_comments", {"messages": newMessages, "room_id": room_id}, broadcast=True)

    if session["chat"] != base64.b64encode(newMessages.encode()):
        session["chat"] = base64.b64encode(newMessages.encode())
        client_socket.emit("new_messages", {"room_id": room_id}, broadcast=True)

    client_socket.emit(pong)


@ client_socket.on("send")
def send(message: str, room_id: int, author_id: int) -> None:
    if message == "\n" or message[0] == " ":
        return

    user = session["special"]
    msg = f"[{time.asctime()}]{user}: "+html.escape(message)
    utils.repeat(
        event="append message",
        return_type=bool,
        data={
            "room_id": room_id,
            "author_id": author_id,
            "author_ip": request.remote_addr,
            "message": msg
        }
    )

    data = {
        "room_id": room_id,
        "message": utils.convert_to_html(msg)
    }
    client_socket.emit("recieve_local_message", data, broadcast=True, include_self=True)
    client_socket.emit("new_messages", data, broadcast=True, include_self=True)


# Get connections
@ client_socket.on("get_online")
def get_online(data: dict) -> None:
    pong = data["pong"]

    client_socket.emit("recieve_online", {"online": user_utils.get_online()})
    client_socket.emit(pong)

# Main


def main() -> None:
    rss.connect()

    atexit.register(rss.disconnect)
    user_utils.clear_online()
    create_routes()
    register_external_receivers()

    app.logger.info(f"STARTED SERVER:\n\tHOST: {HOST}\n\tPORT: {PORT}")
    client_socket.run(app, host=HOST, port=PORT, debug=False)
    client_socket.stop()
    rss.disconnect()


if __name__ == "__main__":
    main()
