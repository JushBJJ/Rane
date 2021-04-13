from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_socketio import SocketIO

import logging

app = None
api = None
socketio = None


def create(config_filename):
    global app
    global api
    global socketio

    # TODO Logging for seperate things such as global message chat, logging in, register, etc
    logging.basicConfig(filename="./logs/server.txt", level=logging.INFO)

    app = Flask(__name__)

    try:
        app.config.from_pyfile(config_filename)
        app.config.from_object("config.SERVER_Development_Home")
    except FileNotFoundError:
        app.config["HOST"] = "0.0.0.0"
        app.config["PORT"] = "5000"

    api = Api(app)
    socketio = SocketIO(app, always_connect=True)
