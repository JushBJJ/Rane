from flask import Flask
from flask_socketio import SocketIO
from multiprocessing import Process
from socketio.exceptions import ConnectionError

import server
import threading

import time
import socket
import socketio

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5001


class WebsiteServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting Website Server")
        server.main()
        print("Stopped Website Server")

    def kill(self):
        self.kill()


app = Flask(__name__)
client = SocketIO(app)
Website = WebsiteServer()

p1 = None


@client.on("start website")
def start_website():
    global p1

    p1 = Process(target=server.main, args=())

    p1.start()
    print("Started Server.")


@client.on("close website")
def close_website():
    global p1

    io = socketio.Client()
    try:
        io.connect(HOST)
    except ConnectionError:
        print("Couldn't connect to server")
    else:
        time.sleep(3)
        io.emit("rss maintenance", {})
        time.sleep(3)
        io.disconnect()

    print("Killing Servers...")
    p1.terminate()

    print("Killed servers, you may press ctrl+c to close running server.")


@client.on("restart website")
def restart_website():
    global p1

    print("Restarting website...")
    close_website()

    print("Closed website.")
    start_website()
    print("Started website.")


if __name__ == "__main__":
    start_website()
    client.run(app, HOST, PORT)
