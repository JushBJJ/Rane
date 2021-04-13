from utils import rss
from flask import request, current_app


def connect() -> None:
    try:
        current_app.logger.info(f"[{request.remote_addr}] Connected to Resource Server.")
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError


def disconnect() -> None:
    try:
        current_app.logger.info(f"[{request.remote_addr}] Disconnected from Resource Server")
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError
