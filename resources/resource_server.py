from flask import Flask
from flask_socketio import SocketIO

import resources.create_rss_app as create_app
import resources.db_utils as db_utils
import shutil

create_app.create("resource_config.py")

app = create_app.app
socketio = create_app.socketio

HOST = app.config["HOST"]
PORT = app.config["PORT"]


@socketio.on("close")
def close(data):
    print("DISCONNECTING...")
    socketio.emit("rss maintenance", {}, broadcast=True)
    socketio.stop()
    exit()


@socketio.on("append message")
def append_message(data):
    def append(cursor):
        message_values = f"\"{author_id}\", \"{author_ip}\", \"{message}\", \"{show}\""
        return db_utils.db_insert(cursor, "Messages", "author_id, author_ip, message, show", message_values)

    room_id = data["room_id"]+".db"

    author_id = data["author_id"]
    author_ip = data["author_ip"]
    message = data["message"]
    show = 1
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(room_id, "rooms", append))


@socketio.on("retrieve messages")
def retrieve_messages(data):
    def retrieve(cursor):
        return db_utils.db_retrieve(cursor,
                                    table="Messages",
                                    select="message",
                                    where="show=1")

    room_id = data["room_id"]+".db"
    received = db_utils.db_edit(room_id, "rooms", retrieve)
    emit = data["emit"]

    messages = [message[0] for message in received]
    socketio.emit(emit, {"messages": messages})


@socketio.on("delete message")
def delete_message(data):
    def delete(cursor):
        return db_utils.db_update(cursor,
                                  table="room_messages",
                                  set_values=set_values,
                                  where=where)

    room_id = data["room_id"]+".db"

    set_values = "show=0"
    where = data["where"]

    return db_utils.db_edit(room_id, "rooms", delete)


@socketio.on("retrieve room info")
def room_info(data):
    def get_info(cursor):
        if where == "":
            return db_utils.db_retrieve_all(cursor, table=table)
        else:
            return db_utils.db_retrieve(cursor, table=table, select=select, where=where)

    room_id = data["room_id"]+".db"

    table = data["table"]
    select = data["select"]
    where = data["where"]
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(room_id, "rooms", get_info))


@socketio.on("select all")
def select_all(data):
    def retrieve(cursor):
        return db_utils.db_retrieve_all(cursor, table=table)

    table = data["table"]
    filename = data["filename"]+".db"
    directory = data["directory"]
    emit = data["emit"]

    socketio.emit(emit, db_utils.db_edit(filename, directory, retrieve))


@socketio.on("update table")
def update_table(data):
    def update(cursor):
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
def append_table(data):
    def append(cursor):
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
def create_room(data):
    def create(cursor):
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
    room_id = data["room_id"]
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

    print(new)
    print(template)

    shutil.copyfile(template, new)
    socketio.emit(emit, db_utils.db_edit(new_filename, "rooms", create))


@socketio.on("delete row")
def delete_row(data):
    def delete(cursor):
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
def truncate_table(data):
    def truncate(cursor):
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
def retrieve_table(data):
    def retrieve(cursor):
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
def is_blacklisted(data):
    def check(cursor):
        return db_utils.db_retrieve(
            cursor,
            table="blacklist",
            select="ip",
            where=f"ip=\"{ip}\""
        )

    ip = data["ip"]
    socketio.emit("check blacklisted", db_utils.db_edit(filename="blacklist", folder="server", function=check))


def main():
    print("STARTED RESOURCE SERVER")
    print("RSS PORT: ", app.config["PORT"])
    socketio.run(app, host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
