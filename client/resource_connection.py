from utils import rss


@rss.rss_socket.on("connect")
def connect():
    try:
        print("Connected to Resource Server.")
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError


@rss.rss_socket.on("disconnect")
def rss_disconnect():
    global disconnect_detected

    try:
        print("Disconnected from Resource Server")
        disconnect_detected = True
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError
