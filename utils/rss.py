from flask import current_app as app

import socket
import asyncio
import socketio as rss

# Connect to Resource server
rss_socket = rss.Client(reconnection=True)
loop = asyncio.get_event_loop()


def connect() -> bool:
    """Connect to resource server."""
    ip = "http://"+socket.gethostbyname(socket.gethostname())+":5001"
    try:
        if not rss_socket.connected:
            rss_socket.connect(ip)
            rss_socket.sleep(2)
        return True
    except Exception as e:
        app.logger.info(e)
        return False


def disconnect() -> bool:
    """Disconnnect from resource server."""
    try:
        rss_socket.disconnect()
        return True
    except Exception as e:
        app.logger.info(e)
        return False


def get_socket() -> rss.Client:
    """Get client."""
    return rss_socket
