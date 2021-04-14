from client import resource_connection as rc
from typing import Any

import resources.create_rss_app as create_app
import resources.db_utils as db_utils
import sqlite3
import shutil

# Create app.
create_app.create("resource_config.py")

app = create_app.app
socketio = create_app.socketio

HOST = app.config["HOST"]
PORT = app.config["PORT"]


def register_external_receivers() -> None:
    """Register connection events."""
    socketio.on_event("connect", rc.connect)
    socketio.on_event("disconnect", rc.disconnect)


@socketio.on("append message")
def append_message(data: dict) -> None:
    """Append message to room database, including the author's id and ip."""
    def append(cursor: sqlite3.Cursor) -> Any:
        message_values = f"\"{author_id}\", \"{author_ip}\", \"{message}\", \"{show}\""
        return db_utils.db_insert(cursor, "Messages", "author_id, author_ip, message, show", message_values)

    room_id = str(data["room_id"])+".db"

    author_id = data["author_id"]
    author_ip = data["author_ip"]
    message = data["message"]
    show = 1
    emit = data["emit"]

    app.logger.info(f"New message from {author_id} ({author_ip}): {message}")
    socketio.emit(emit, db_utils.db_edit(room_id, "rooms", append))


@socketio.on("retrieve messages")
def retrieve_messages(data: dict) -> None:
    """Get all messages from a room."""
    def retrieve(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve(cursor,
                                    table="Messages",
                                    select="message",
                                    where="show=1")

    room_id = str(data["room_id"])+".db"
    received = db_utils.db_edit(room_id, "rooms", retrieve)
    emit = data["emit"]

    messages = [message[0] for message in received]
    socketio.emit(emit, {"messages": messages})


@socketio.on("delete message")
def delete_message(data: dict) -> None:
    """Stop a message from showing."""
    # TODO
    def delete(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_update(cursor,
                                  table="room_messages",
                                  set_values=set_values,
                                  where=where)

    room_id = str(data["room_id"])+".db"

    set_values = "show=0"
    where = data["where"]

    return db_utils.db_edit(room_id, "rooms", delete)


@socketio.on("retrieve room info")
def room_info(data: dict) -> None:
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
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(room_id, "rooms", get_info))


@socketio.on("select all")
def select_all(data: dict) -> None:
    """Select all data from a table."""
    def retrieve(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve_all(cursor, table=table)

    table = data["table"]
    filename = data["filename"]+".db"
    directory = data["directory"]
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(filename, directory, retrieve))


@socketio.on("update table")
def update_table(data: dict) -> None:
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
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(filename, folder, update))


@socketio.on("append table")
def append_table(data: dict) -> None:
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
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(filename, folder, append))


@socketio.on("create room")
def create_room(data: dict) -> None:
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
    emit = data["emit"]

    tables = {
        "Admins": {
            "columns": "Username, ID",
            "values": f"\"{owner}\",\"{owner_id}\""
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
    socketio.emit(emit, db_utils.db_edit(new_filename, "rooms", create))


@socketio.on("delete row")
def delete_row(data: dict) -> None:
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
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(filename, folder, delete))


@socketio.on("truncate")
def truncate_table(data: dict) -> None:
    """Truncate everything from a table."""
    def truncate(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_truncate(
            cursor,
            table=table
        )

    filename = data["filename"]+".db"
    folder = data["folder"]
    table = data["table"]
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(filename, folder, truncate))


@ socketio.on("retrieve table")
def retrieve_table(data: dict) -> None:
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
    emit = data["emit"]

    table = data["table"]
    select = data["select"]
    where = data["where"]

    socketio.emit(emit, db_utils.db_edit(filename, folder, retrieve))


@ socketio.on("is blacklisted")
def is_blacklisted(data: dict) -> None:
    """Check if user is blacklisted from the website."""
    def check(cursor: sqlite3.Cursor) -> Any:
        return db_utils.db_retrieve(
            cursor,
            table="blacklist",
            select="ip",
            where=f"ip=\"{ip}\""
        )

    ip = data["ip"]
    socketio.emit("check blacklisted", db_utils.db_edit(filename="blacklist", folder="server", function=check))


def main():
    register_external_receivers()

    app.logger.info(f"STARTED RESOURCE SERVER\n\tHOST: {HOST}\n\tPORT: {PORT}")
    socketio.run(app, host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
