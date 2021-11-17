from flask import current_app as app
from typing import Any

import resources.db_utils as db_utils
import sqlite3
import shutil


def get_user_by_id(data: dict) -> Any:
    user_id = data["id"]

    data = {
        "filename": "accounts",
        "folder": "server",
        "table": "accounts",
        "select": "username",
        "where": f"\"id\"=\"{user_id}\""
    }

    try:
        return retrieve_table(data)[0][0]
    except Exception as e:
        return False


def get_id_by_user(data: dict) -> Any:
    username = data["username"]

    data = {
        "filename": "accounts",
        "folder": "server",
        "table": "accounts",
        "select": "id",
        "where": f"\"username\"=\"{username}\""
    }

    try:
        return retrieve_table(data)[0][0]
    except IndexError:
        return False


def join_room(data: dict) -> bool:
    """Append a new user into a room."""
    def join(cursor: sqlite3.Cursor) -> Any:
        member_values = f"\"{user_id}\", \"{username}\", \"Member\""
        return db_utils.db_insert(cursor, "Members", "\"ID\", \"Username\", \"Role\"", member_values)

    room_id = str(data["room_id"])+".db"
    user_id = data["user_id"]

    username = get_user_by_id({"id": user_id})

    if not username:
        return False

    app.logger.info(f"User {user_id} has joined room {room_id}")
    return db_utils.db_edit(room_id, "rooms", join)


def append_message(data: dict) -> bool:
    """Append message to room database, including the author's id and ip."""
    def append(cursor: sqlite3.Cursor) -> Any:
        message_values = f"\"{author_id}\", \"{author_ip}\", \"{message}\", \"{media}\",\"{show}\""
        return db_utils.db_insert(cursor, "Messages", "author_id, author_ip, message, media, show", message_values)

    room_id = str(data["room_id"])+".db"

    author_id = data["author_id"]
    author_ip = data["author_ip"]
    message = data["message"]
    media = data["media"]
    show = 1

    app.logger.info(f"New message from {author_id} ({author_ip}): {message}")
    return db_utils.db_edit(room_id, "rooms", append)


def retrieve_messages(data: dict) -> tuple:
    """Get all messages including their media child from a room."""
    def retrieve(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve(cursor,
                                    table="Messages",
                                    select="message, media",
                                    where="show=1")

    room_id = str(data["room_id"])+".db"
    received = db_utils.db_edit(room_id, "rooms", retrieve)

    try:
        """
        [(a, 1), (b, 2), (c, 3)] -> (a, b, c), (1,2,3)
        """
        messages, medias = zip(*received)  # Split messages and medias
    except ValueError:
        return (), ()

    return messages, medias


def delete_message(data: dict) -> bool:
    """Stop a message from showing."""
    def delete(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_update(cursor,
                                  table="room_messages",
                                  set_values=set_values,
                                  where=where)

    room_id = str(data["room_id"])+".db"

    set_values = "show=0"
    where = data["where"]

    return db_utils.db_edit(room_id, "rooms", delete)


def retrieve_room_info(data: dict) -> list[Any]:
    """Get all room info from database."""
    def get_info(cursor: sqlite3.Cursor) -> Any:
        if where == "":
            return db_utils.db_retrieve_all(cursor, table=table)
        else:
            return db_utils.db_retrieve(cursor, table=table, select=select, where=where)

    room_id = str(data["room_id"])+".db"

    table = data["table"]
    select = data["select"]
    where = data["where"]

    return db_utils.db_edit(room_id, "rooms", get_info)


def select_all(data: dict) -> list[Any]:
    """Select all data from a table."""
    def retrieve(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve_all(cursor, table=table)

    table = data["table"]
    filename = data["filename"]+".db"
    directory = data["directory"]

    return db_utils.db_edit(filename, directory, retrieve)


def update_table(data: dict) -> bool:
    """Update table values."""
    def update(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_update(
            cursor,
            table=table,
            set_values=set_values,
            where=where
        )

    filename = data["filename"]+".db"
    folder = data["folder"]
    table = data["table"]
    set_values = data["set_values"]
    where = data["where"]

    return db_utils.db_edit(filename, folder, update)


def append_table(data: dict) -> bool:
    """Add new table values."""
    def append(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_insert(
            cursor,
            table=table,
            columns=columns,
            values=values,
            unique=unique
        )

    filename = data["filename"]+".db"
    folder = data["folder"]
    table = data["table"]
    columns = data["columns"]
    values = data["values"]
    unique = data["unique"]

    return db_utils.db_edit(filename, folder, append)


def create_room(data: dict) -> list:
    """Create a new room."""
    def create(cursor: sqlite3.Cursor) -> Any:
        returns = []
        for table in tables.keys():
            returns.append(
                db_utils.db_insert(
                    cursor,
                    table=table,
                    columns=tables[table]["columns"],
                    values=tables[table]["values"]
                )
            )
        return returns

    name = data["name"]
    owner = data["owner"]

    owner_id = data["owner_id"]
    room_id = str(data["room_id"])

    tables = {
        "Members": {
            "columns": "ID, Username, \"Role\"",
            "values": f"\"{owner_id}\", \"{owner}\",\"Room Owner\""
        },
        "Owners": {
            "columns": "Username, ID",
            "values": f"\"{owner}\",\"{owner_id}\""
        },
        "Name": {
            "columns": "Name",
            "values": f"\"{name}\""
        }
    }

    # Copy File
    new_filename = f"{room_id}.db"
    template = db_utils.correct_path(".", "room_template.db")
    new = db_utils.correct_path("rooms", new_filename)

    shutil.copyfile(template, new)
    return db_utils.db_edit(new_filename, "rooms", create)


def delete_row(data: dict) -> bool:
    """Delete a row from a table."""
    def delete(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_delete(
            cursor,
            table=table,
            where=where
        )

    filename = data["filename"]+".db"
    folder = data["folder"]
    table = data["table"]
    where = data["where"]

    return db_utils.db_edit(filename, folder, delete)


def truncate_table(data: dict) -> bool:
    """Truncate everything from a table."""
    def truncate(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_truncate(
            cursor,
            table=table
        )

    filename = data["filename"]+".db"
    folder = data["folder"]
    table = data["table"]

    return db_utils.db_edit(filename, folder, truncate)


def retrieve_table(data: dict) -> list[Any]:
    """Get all info from a table."""
    def retrieve(cursor: sqlite3.Cursor) -> Any:
        ret = db_utils.db_retrieve(
            cursor,
            table=table,
            select=select,
            where=where
        )
        return ret

    filename = data["filename"]+".db"
    folder = data["folder"]

    table = data["table"]
    select = data["select"]
    where = data["where"]

    return db_utils.db_edit(filename, folder, retrieve)


def is_blacklisted(data: dict) -> list[Any]:
    """Check if user is blacklisted from the website."""
    def check(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve(
            cursor,
            table="blacklist",
            select="ip",
            where=f"ip=\"{ip}\""
        )

    ip = data["ip"]
    return db_utils.db_edit(filename="blacklist", folder="server", function=check)


def get_password(data: dict) -> list:
    """Get password from user"""
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

# Similar to get_password, do the same but get the username instead.


def get_username(data: dict) -> list:
    """Get username from user"""
    def db_check_username(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve(
            cursor,
            table="accounts",
            select="username",
            where=f"username=\"{username}\""
        )
    username = data["username"]
    folder = "server"
    return db_utils.db_edit(filename="accounts.db", folder=folder, function=db_check_username)
