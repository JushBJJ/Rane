"""Main Website Server"""
from utils import room_utils, user_utils, rss, utils, chat_utils
from routes.create_routes import create_routes
from client import website_connection as wc
from flask import session, request, jsonify
from routes.auth import auth

import create_app
import hashlib
import secrets
import base64
import time
import html
import os

create_app.create("config.py")

app = create_app.app
api = create_app.api
client_socket = create_app.socketio
HOST = app.config["HOST"]
PORT = app.config["PORT"]

api.add_resource(auth.Authorize, "/api/authorize")


def register_external_receivers() -> None:
    """Register socket event handlers."""
    client_socket.on_event("disconnect", wc.client_disconnected)
    client_socket.on_event("connect", wc.client_connect)
    client_socket.on_event("connected", wc.connected)
    client_socket.on_event("rss maintenance", wc.client_maintenance)

# Client-side
# Rooms Functions

# TODO


@app.route("/create_room", methods=["POST"])
def create_room():
    """Create new room, public or private."""
    name = html.escape(request.form["name"])
    desc = html.escape(request.form["description"])
    password = html.escape(request.form["password"])
    public = int(request.form["public"] == "Public")
    owner = session["username"]

    owner_id = user_utils.get_account_info(owner)[4]
    new_room_id = base64.b64encode(str(secrets.randbits(128)).encode()).decode()

    # Append new room info.
    ret = utils.call_db(
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
    returns = utils.call_db(
        event="create room",
        return_type=list,
        data={
            "name": name,
            "owner": owner,
            "owner_id": owner_id,
            "room_id": new_room_id
        }
    )

    return jsonify({"success": ret and all(r == True for r in returns)})


@ client_socket.on("get_rooms")
def get_rooms(data: dict) -> None:
    """Get all rooms if the user is whitelisted or room is public."""
    pong = data["pong"]

    # user_utils.get_user_rooms(session["username"])

    rooms = room_utils.get_rooms()
    section = ""

    # room_utils.get_user_rooms(session["username"])

    # Create div blocks for each room.
    for room in rooms:
        section += f"""
        <div class="h-auto pb-4">
            <a class="block" onclick=\'move_room(\"{room[2]}\",\"{room[0]}\")\'>
                <div class="card rounded-xl has-background-black p-2.5 room">
                    <div class="media-content">
                        <p class="title is-4 has-text-centered">{room[0]}</p>
                        <p class="subtitle is-5 has-text-centered"><i>{room[1]}</i></p>
                    </div>
                </div>
            </a>
        </div>
        """

    client_socket.emit("recieve_rooms", {"rooms": section}, broadcast=True, include_self=True)
    client_socket.emit(pong)

# Messages


@ client_socket.on("new message")
def get_new_message(data: dict) -> None:
    """Get new message."""
    # TODO For specific rooms.
    room_id = data["room_id"]
    message = data["message"]

    # Receive 1 message directly to client.
    client_socket.emit("recieve_local_message", data)


@ client_socket.on("get_messages")
def get_messages(data: dict) -> None:
    """Get all messages of a room."""
    room_id = data["params"]
    pong = data["pong"]

    messages, medias = room_utils.get_room_messages(room_id)
    newMessages = ""

    try:
        for message, media in zip(messages, medias):
            media = utils.convert_media_to_html(media)
            timestamp, message = utils.convert_to_html(message, room_id, session["username"])

            newMessages += timestamp+message+media
    except ValueError:
        return  # No need to process anything, there aren't any messages.

    # Send all messages of the room to the client.
    client_socket.emit("recieve_messages", {"messages": newMessages, "room_id": room_id}, broadcast=True, include_self=True)

    # Scroll user down to the bottom.
    if session["chat"] != base64.b64encode(newMessages.encode()):
        session["chat"] = base64.b64encode(newMessages.encode())
        client_socket.emit("new_messages", {"room_id": room_id}, broadcast=True, include_self=True)

    client_socket.emit(pong)


@ app.route("/send", methods=["POST"])
def send():
    """Send new message to a room."""
    files = request.files
    message = request.form["message"]
    room_id = request.form["room_id"]
    author_id = request.form["user_id"]

    message = message.replace("\n", "")

    # return jsonify({}) if the length of files is 0 or if the message is just a space, invalid ascii or just nothing
    if len(files) == 0 and (message.isspace() or not message.isascii() or message == "\n" or message == ""):
        return jsonify({})

    path = ""
    try:
        media = files["file"]
        path = os.path.join(app.config["uploadFolder"], media.filename)
        media.save(path)
        path = "/static/uploads/"+media.filename
    except Exception as e:
        app.logger.info(f"Exception when uploading file: {e}")

    user = session["username"]
    msg = f"[{time.asctime()}]{user}: "+html.escape(message)

    # Append message to room database.
    utils.call_db(
        event="append message",
        return_type=bool,
        data={
            "room_id": room_id,
            "author_id": author_id,
            "author_ip": request.remote_addr,
            "message": msg,
            "media": path
        }
    )

    media = utils.convert_media_to_html(path)
    timestamp, msg = utils.convert_to_html(msg, room_id, session["username"])
    message = timestamp+msg+media

    data = {
        "room_id": room_id,
        "message": message
    }

    client_socket.emit("recieve_local_message", data, broadcast=True, include_self=True)
    client_socket.emit("new_messages", data, broadcast=True, include_self=True)
    return jsonify({})


@ app.route("/change_password", methods=["POST"])
def change_password():
    """Change the password of a user."""
    old_password = hashlib.sha256(request.form["old_password"].encode()).hexdigest()
    new_password = hashlib.sha256(request.form["new_password"].encode()).hexdigest()

    user = session["username"]
    if not utils.check_password(user, old_password):
        return jsonify({"success": False, "message": "Wrong password."})

    utils.change_password(user, new_password)
    return jsonify({"success": True, "message": "Password changed."})

# Change username, similar to change_password


@ app.route("/change_username", methods=["POST"])
def change_username():
    """Change the username of a user."""
    old_username = session["username"]
    new_username = request.form["new_username"]

    if new_username == old_username:
        return jsonify({"success": False, "message": "New username is the same as the old username."})
    elif utils.check_username(new_username):
        return jsonify({"success": False, "message": "Username already exists."})

    utils.change_username(old_username, new_username)
    session["username"] = new_username
    time.sleep(1)
    return jsonify({"success": True, "message": "Username changed.", "username": new_username})

# Get connections


@ client_socket.on("get_online")
def get_online(data: dict) -> None:
    """Get all current connections."""
    pong = data["pong"]

    client_socket.emit("recieve_online", {"online": user_utils.get_online()}, broadcast=True, include_self=True)
    client_socket.emit(pong)


@ client_socket.on("recolor")
def recolor(data) -> None:
    pong = data["pong"]
    room_id = data["params"]

    chat_utils.autocolor(room_id)
    client_socket.emit(pong)
# Main


def main() -> None:
    """Start up server."""
    user_utils.clear_online()

    create_routes()
    register_external_receivers()

    app.logger.info(f"STARTED SERVER:\n\tHOST: {HOST}\n\tPORT: {PORT}")
    client_socket.run(app, host=HOST, port=PORT, debug=False)
    client_socket.stop()

    rss.disconnect()


if __name__ == "__main__":
    main()
