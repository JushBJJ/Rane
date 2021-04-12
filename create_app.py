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
    app.config.from_pyfile(config_filename)
    app.config.from_object("config.Development_Home")

    api = Api(app)
    socketio = SocketIO(app, logger=True, always_connect=True)
