"""Main Website Server, requires resource server in order to run."""
from utils import room_utils, user_utils, rss, utils
from routes.create_routes import create_routes
from client import website_connection as wc
from flask import session, request
from routes.auth import auth

import create_app
import secrets
import base64
import atexit
import time
import html


create_app.create("config.py")

app = create_app.app
api = create_app.api
client_socket = create_app.socketio
HOST = app.config["HOST"]
PORT = app.config["PORT"]

api.add_resource(auth.authorize, "/api/authorize")


def register_external_receivers() -> None:
    """Register socket event handlers."""
    client_socket.on_event("disconnect", wc.client_disconnected)
    client_socket.on_event("connect", wc.client_connect)
    client_socket.on_event("connected", wc.connected)
    client_socket.on_event("rss maintenance", wc.client_maintenance)

# Client-side
# Rooms Functions


@ client_socket.on("create room")
def create_room(args: dict) -> bool:
    """Create new room, public or private."""
    name = html.escape(args["name"])
    desc = html.escape(args["desc"])
    public = int(args["public"] == "Public")
    owner = args["owner"]

    owner_id = user_utils.get_account_info(owner)[4]
    new_room_id = base64.b64encode(str(secrets.randbits(128)).encode()).decode()

    # Append new room info.
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

    # Create room database.
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
    """Get all rooms if the user is whitelisted or room is public."""
    pong = data["pong"]

    rooms = room_utils.get_rooms()
    section = ""

    # Create div blocks for each room.
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


@client_socket.on("new message")
def get_new_message(data: dict) -> None:
    """Get new message."""
    # TODO For specific rooms.
    room_id = data["room_id"]
    message = data["message"]

    # Receive 1 message directly to client.
    client_socket.emit("recieve_local_message", data)


@client_socket.on("get_messages")
def get_messages(data: dict) -> None:
    """Get all messages of a room."""
    room_id = data["params"]
    pong = data["pong"]

    messages = room_utils.get_room_messages(room_id)
    newMessages = ""

    for message in messages["messages"]:
        newMessages += utils.convert_to_html(message)

    # Send all messages of the room to the client.
    client_socket.emit("recieve_messages", {"messages": newMessages, "room_id": room_id}, broadcast=True)

    # Scroll user down to the bottom.
    if session["chat"] != base64.b64encode(newMessages.encode()):
        session["chat"] = base64.b64encode(newMessages.encode())
        client_socket.emit("new_messages", {"room_id": room_id}, broadcast=True)

    client_socket.emit(pong)


@ client_socket.on("send")
def send(message: str, room_id: int, author_id: int) -> None:
    """Send new message to a room."""
    # Prevent user from sending blank messages
    if message == "\n" or message[0] == " ":
        return

    user = session["special"]
    msg = f"[{time.asctime()}]{user}: "+html.escape(message)

    # Append message to room database.
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
    """Get all current connections."""
    pong = data["pong"]

    client_socket.emit("recieve_online", {"online": user_utils.get_online()})
    client_socket.emit(pong)

# Main


def main() -> None:
    """Start up server."""
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
