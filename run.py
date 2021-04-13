from flask_socketio import SocketIO
from flask import Flask
from multiprocessing import Process

import threading
import server
import resources.resource_server as resource_server
import eventlet

import time

HOST = "192.168.1.10"
PORT = 5002


class RSSServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting RSS Server")
        resource_server.main()
        print("Stopped RSS Server")

    def kill(self):
        self.kill()


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
RSS = RSSServer()
Website = WebsiteServer()

p1 = Process(target=resource_server.main, args=())
p2 = Process(target=server.main, args=())


@client.on("close website")
def close_website():
    print("Killing Servers...")
    p1.terminate()
    p2.terminate()

    print("Killing client. You may not press ctrl+c")
    client.stop()
    print("Fully killed client.")


if __name__ == "__main__":
    print("Starting RSS Server.")
    p1.start()
    time.sleep(3)

    print("Starting Website Server")
    p2.start()

    client.run(app, HOST, PORT)

    p1.join()
    p2.join()
