from logging.handlers import SocketHandler
from flask import Flask
from flask_restful import Api
from flask_socketio import SocketIO

import socket
import logging

app = None
api = None
socketio = None


def create(config_filename: str) -> None:
    """Create app by config."""
    global app
    global api
    global socketio

    # TODO Logging for seperate things such as global message chat, logging in, register, etc

    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename="./logs/website_log.txt", level=logging.INFO)
    app = Flask(__name__)

    try:
        app.config.from_pyfile(config_filename)
        app.config.from_object("config.SERVER_Development_Home")
    except FileNotFoundError:
        host_ip = socket.gethostbyname(socket.gethostname())
        app.config["HOST"] = host_ip
        app.config["PORT"] = 5000
        app.config["SECRET_KEY"] = "dadada"

    api = Api(app)
    socketio = SocketIO(app)
