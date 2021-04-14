from socketio.exceptions import ConnectionRefusedError
from flask import request, current_app
from utils import rss


def connect() -> None:
    """Log new connection of the resource server."""
    try:
        current_app.logger.info(f"[{request.remote_addr}] Connected to Resource Server.")
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError


def disconnect() -> None:
    """Log disconnection of the resource server."""
    try:
        current_app.logger.info(f"[{request.remote_addr}] Disconnected from Resource Server")
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError
