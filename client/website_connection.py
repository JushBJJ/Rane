from flask import session
from utils import user_utils, chat_utils
from datetime import datetime

import routes.gateway as routes
import create_app
import time


app = create_app.app

client_socket = create_app.socketio


@ client_socket.on("disconnect")
def client_disconnected():
    client_socket.emit("clear tasks")
    print("\n\nCLIENT DISCONNECTED\n\n")
    client_socket.stop()
    user_utils.monitor_activity(session["username"])


@ client_socket.on("connect")
def client_connect():
    print("\n\nCLIENT CONNECTED\n\n")


@ client_socket.on("connected")
def connected(data):
    room_id = data["params"]
    pong = data["pong"]

    if routes.gateway():
        chat_utils.log(f"[{time.asctime()}]<span class=\"server\">SERVER: " + session["username"] + " has been banned."+"</span>", str(room_id))
        client_socket.emit("redirect")
        return
    elif "anything" not in session:
        session["anything"] = ""
        session["login_error"] = ""
        session["register_error"] = ""
        session["username"] = ""
        session["chat"] = ""
        session["room_id"] = ""
        client_socket.emit("redirect")
        return

    user_utils.status(session["username"], "Joined")
    seen = user_utils.get_account_info(session["username"])[3]

    if (datetime.now().minute - user_utils.convert_to_datetime(seen).minute) >= 10:
        user_utils.online(1, str(room_id))
    else:
        user_utils.online(1, str(room_id), silent=True)

    client_socket.emit(pong)


@client_socket.on("rss maintenance")
def client_maintenance(data):
    print("MAINTENANCE")
    client_socket.emit("maintenance", {})
    client_socket.stop()
