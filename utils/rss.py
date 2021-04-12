import socketio as rss
import asyncio

# Connect to Resource server
rss_socket = rss.Client(reconnection=True)
loop = asyncio.get_event_loop()


def connect():
    try:
        if not rss_socket.connected:
            rss_socket.connect("http://127.0.0.1:5001/")
            rss_socket.sleep(2)
        return True
    except Exception as e:
        print(e)
        return False


def disconnect():
    try:
        rss_socket.disconnect()
        return True
    except Exception as e:
        print(e)
        return False


def get_socket():
    return rss_socket
