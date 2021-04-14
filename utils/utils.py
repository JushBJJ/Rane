from typing import Any
import flask
from flask import request
from flask import current_app as app
from flask import session

from utils import rss

import datetime
import secrets
import time


def get_ip() -> str:
    """Get connected user IP."""
    return request.remote_addr


def get_session() -> session:
    """Get current session."""
    return session


def get_app() -> flask.Flask:
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


def repeat(event: str, return_type: Any, **kwargs) -> Any:
    """
    For socketio functions.

    Args:
        event (string): Server-side socket function.
        return_type (type): Type that should be returned.
    """
    event_get = secrets.token_urlsafe()

    @rss.rss_socket.on(event_get)
    def event_func(data: Any) -> None:
        """Socketio event."""
        nonlocal returned
        nonlocal run
        nonlocal event

        returned = None

        if data == False:
            app.logger.info(f"[{event}] Operation failed. Retrying in 5 seconds...")
            app.logger.info(f"[{event}] Operation data: {data}")
            run = False
            rss.rss_socket.sleep(5)
            run = True
        elif type(data) == return_type:
            returned = data
        else:
            app.logger.info(f"[{event}] Wrong type returned: {type(data)}, expected {return_type}.")
            app.logger.info(f"[{event}] Operation data: {data}")

    def wrapper() -> Any:
        nonlocal returned
        nonlocal run
        returned = None

        run = True
        retry = 0

        while True:
            # Loop until returned variable is not None or False.
            if returned == None:
                returned = None

                # Emit message to resource server.
                if run:
                    rss.rss_socket.emit(event=event, data=kwargs["data"])
                    rss.rss_socket.sleep(0)
                    run = False
                    continue

                # Retry every 30th second
                b = datetime.datetime.now()

                if(b.second % 30) == 0:
                    run = True
                    retry += 1

                    if retry >= 10:
                        break

                    app.logger.info(f"[{event_get}] Retrying operation...")
                    time.sleep(2)

            elif returned == False:
                app.logger.info(f"[{event_get}] Function failed. Trying again...")
                returned = None
            else:
                break

        ret = returned
        returned = None
        return ret

    kwargs["data"]["emit"] = event_get
    returned = None
    run = True
    return wrapper()
