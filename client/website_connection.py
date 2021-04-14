from flask import session, request
from flask import current_app as app
from utils import user_utils, chat_utils
from datetime import datetime

import routes.gateway as routes
import create_app
import time


def client_disconnected() -> None:
    """Clear tasks and forcefully disconnect user from the websocket client then monitor activity."""
    client_socket = create_app.socketio

    client_socket.emit("clear tasks")
    client_socket.emit("force disconnect")

    app.logger.info(f"[{request.remote_addr}]CLIENT DISCONNECTED")
    user_utils.monitor_activity(session["username"])


def client_connect() -> None:
    """Log when client is connected to the server."""
    app.logger.info(f"[{request.remote_addr}]CLIENT CONNECTED")


def connected(data: dict) -> None:
    """Set status of user when they connect to a room."""
    client_socket = create_app.socketio
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
        user_utils.online(1, room_id)
    else:
        user_utils.online(1, room_id, silent=True)

    client_socket.emit(pong)


def client_maintenance(data: dict) -> None:
    """Switch all clients to maintenance mode."""
    client_socket = create_app.socketio
    app.logger.info("CLIENT RAISED MAINTENANCE MODE")
    client_socket.emit("maintenance", {}, broadcast=True, include_self=True)
