import socketio as rss
import asyncio

from flask import current_app as app
# Connect to Resource server
rss_socket = rss.Client(reconnection=True)
loop = asyncio.get_event_loop()


def connect():
    try:
        if not rss_socket.connected:
            rss_socket.connect("http://192.168.1.10:5001/")
            rss_socket.sleep(2)
        return True
    except Exception as e:
        app.logger.info(e)
        return False


def disconnect():
    try:
        rss_socket.disconnect()
        return True
    except Exception as e:
        app.logger.info(e)
        return False


def get_socket():
    return rss_socket
