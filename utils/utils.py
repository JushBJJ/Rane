from typing import Any
from flask import current_app as app
from utils import rss
from flask import request, session, Flask
from resources import db

import time
import inspect
import secrets
import datetime


def get_ip() -> str:
    """Get connected user IP."""
    return request.remote_addr


def get_session() -> session:
    """Get current session."""
    return session


def get_app() -> Flask:
    """Get current app."""
    return app


def convert_to_html(message: str) -> str:
    """Convert messages into html."""
    # Split time
    # TODO alternative to time in the message string.
    msgSplit = ("".join(message.split("["))).split("]")
    msgTime = msgSplit[0]
    content = "".join(msgSplit[1:])

    newMessage = "<p class=\"msg-time\">"+msgTime+"</p><div class=\"bubble\"><div class=\"message\">"+content+"</div></div>"
    return newMessage


def call_db(event: str, return_type: Any, **kwargs) -> Any:
    """
    Call functions from resources/db.py

    Args:
        event (str): The function to be called.
        return_type (Any): Return type.
    """

    # TODO (Possibly try to change every line of code containing a space from other files to underscore)

    # Replace " " with "_"
    event = "".join("_"+s for s in event.split())[1:]

    # Find function (Quick bi-directional find)
    functions = inspect.getmembers(db, inspect.isfunction)

    back = 0
    front = len(functions)-1

    function = None

    for _ in range(front):
        if functions[front][0] == event:
            function = functions[front][1]
            break
        elif functions[back][0] == event:
            function = functions[back][1]
            break

        front -= 1
        back += 1

    # Call function
    return False if function == None else function(kwargs["data"])
