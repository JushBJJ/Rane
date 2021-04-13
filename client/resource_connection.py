from utils import rss
from flask import request, current_app


@rss.rss_socket.on("connect")
def connect():
    try:
        current_app.logger.info(f"[{request.remote_addr}] Connected to Resource Server.")
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError


@rss.rss_socket.on("disconnect")
def rss_disconnect():
    global disconnect_detected

    try:
        current_app.logger.info(f"[{request.remote_addr}] Disconnected from Resource Server")
        disconnect_detected = True
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError
