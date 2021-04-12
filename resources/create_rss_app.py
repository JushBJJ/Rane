from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_socketio import SocketIO
import os

import logging

app = None
api = None
socketio = None
basedir = os.path.abspath(os.path.dirname(__file__))


def create(config_filename):
    global app
    global api
    global socketio

    # TODO Logging for seperate things such as global message chat, logging in, register, etc
    logging.basicConfig(filename="logs.txt", level=logging.INFO)

    app = Flask(__name__)
    app.config.from_pyfile(f"{basedir}/{config_filename}")
    app.config.from_object("resources.resource_config.RSS_Development_Home")

    api = Api(app)
    socketio = SocketIO(app, logger=True, always_connect=True)
