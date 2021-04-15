from flask import Flask
from flask_restful import Api
from flask_socketio import SocketIO
from logging.handlers import SocketHandler
import os
import socket

import logging

app = None
api = None
socketio = None
basedir = os.path.abspath(os.path.dirname(__file__))


def create(config_filename: str) -> None:
    global app
    global api
    global socketio

    # TODO Logging for seperate things such as global message chat, logging in, register, etc
    log = logging.basicConfig(format='%(asctime)s %(message)s',
                              datefmt='%m/%d/%Y %I:%M:%S %p',
                              filename="../logs/rss_server.txt",
                              level=logging.INFO)

    app = Flask(__name__)
    try:
        app.config.from_pyfile(f"{basedir}/{config_filename}")
        app.config.from_object("resources.resource_config.RSS_Development_Home")
    except FileNotFoundError:
        app.config["HOST"] = socket.gethostbyname(socket.gethostname())
        app.config["PORT"] = "5001"
        app.config["SECRET_KEY"] = "dadada"

    api = Api(app)
    socketio = SocketIO(app, always_connect=True, logger=True)
