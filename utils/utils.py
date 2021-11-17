from typing import Any

from flask import current_app as app
from flask import request, session, Flask

from utils import room_utils
from resources import db

import inspect
import os

# Support Filetypes. .gif/.jiff is considered as an "image" because <img> supports gif's, but not .mp4
support_types = (".webm", ".mp4", ".mpeg", ".jpg", ".jpeg", ".png", ".gif", ".jiff")


def get_ip() -> str:
    """Get connected user IP."""
    return request.remote_addr


def get_session() -> session:
    """Get current session."""
    return session


def get_app() -> Flask:
    """Get current app."""
    return app


def convert_to_html(message: str, room_id: str, username: str) -> tuple:
    """
    Convert messages into html.

    FORMAT: "[time] (user): (message)"
    """
    # Split time
    # TODO alternative to time in the message string.
    msgSplit = ("".join(message.split("["))).split("]")
    msgTime = msgSplit[0]
    content = "".join(msgSplit[1:])

    # Get room roles
    user_id = db.get_id_by_user({"username": username})
    roles = room_utils.get_room_info(room_id, "Members", "\"Role\"", f"ID=\"{user_id}\"")

    if roles == []:
        roles = [["Member"]]

    # TODO multiple roles
    timestamp = f"""
        <p class=\"tag is-black mt-2.5\">{msgTime}</p>
        <p class=\"tag is-black mt-2.5\">{roles[0][0]}</p>
    """
    newMessage = f"""<div class=\"border border-gray-900 rounded-md p-2.5 pr-2.5 pt-0.5 pb-0.5 w-max\">{content}</div>"""

    return timestamp, newMessage


def convert_media_to_html(path: str) -> str:
    """
    convert_image_to_html

    Args:
        path (str): Path of the media

    Returns:
        str: HTML block
    """

    if path.endswith((support_types)):
        return f"""
            <figure class="image is-16by9">
                <iframe class="has-ratio" width="640" height="360" src="{path}" frameborder="0" allowfullscreen sandbox></iframe>
            </figure>
        """

    elif path == "":
        return ""
    else:
        filename = os.path.basename(path)
        return f"""
            <a class="button is-black is-text" href="{path}" download="{filename}">{filename}</a>
            <br>
        """


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


# Here is the check_password function definition:
"""
def get_password(data: dict) -> bool:
    # Get password from user
    def db_check_password(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve(
            cursor,
            table="accounts",
            select="password",
            where=f"username=\"{username}\""
        )

    username = data["username"]
    folder = "server"
    return db_utils.db_edit(filename="accounts.db", folder=folder, function=db_check_password)
"""


def check_password(username: str, password: str) -> bool:
    user_password = db.get_password({"username": username})
    # The value format the user_password is in is [('password')]
    # Get the password
    return user_password[0][0] == password


def change_password(username: str, new_password: str) -> bool:
    # Update table
    return db.update_table({
        "filename": "accounts",
        "folder": "server",
        "table": "accounts",
        "set_values": f"\"password\"=\"{new_password}\"",
        "where": f"username=\"{username}\""
    })

# Similar to check_password and change_password do the same but username


def check_username(username: str) -> bool:
    return db.get_username({"username": username}) != []


def change_username(username: str, new_username: str) -> bool:
    # Update table
    return db.update_table({
        "filename": "accounts",
        "folder": "server",
        "table": "accounts",
        "set_values": f"\"username\"=\"{new_username}\"",
        "where": f"username=\"{username}\""
    })
