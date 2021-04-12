from flask import *
from datetime import datetime
from socketio.exceptions import ConnectionRefusedError

import requests
from utils import room_utils, user_utils, chat_utils, rss, utils

import create_app
import auth

import time
import base64
import os
import hashlib
import html
import secrets
import atexit


create_app.create("config.py")

app = create_app.app
api = create_app.api
client_socket = create_app.socketio
HOST = app.config["HOST"]
PORT = app.config["PORT"]

api.add_resource(auth.authorize, "/api/authorize")

disconnect_detected = False


@client_socket.on("rss maintenance")
def client_maintenance(data):
    print("MAINTENANCE")
    client_socket.emit("maintenance", {})
    client_socket.stop()


@app.route("/maintenance")
def page_maintenance():
    return render_template("maintenance.html")


@rss.rss_socket.on("message sent")
def message_sent(data):
    client_socket.emit("force", {"name": "get_comments", "params": data["room_id"]})


@ app.route("/")
def main():
    if gateway() == True:
        app.logger.info(f"{request.remote_addr} connected to enter the server.")
        return render_template("banned.html")

    if "anything" not in session:
        session["anything"] = ""
        session["loginError"] = ""
        session["registerError"] = ""
        session["username"] = ""
        session["chat"] = ""
        session["room_id"] = 0

    return render_template("login.html",
                           loginError=session["loginError"],
                           registerError=session["registerError"])


@rss.rss_socket.on("connect")
def connect():
    try:
        print("Connected to Resource Server.")
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError


@rss.rss_socket.on("disconnect")
def rss_disconnect():
    global disconnect_detected

    try:
        print("Disconnected from Resource Server")
        disconnect_detected = True
    except ConnectionRefusedError:
        rss.disconnect()
        raise ConnectionRefusedError


@ client_socket.on("connected")
def connected(data):
    room_id = data["params"]
    pong = data["pong"]

    if gateway():
        chat_utils.log(f"[{time.asctime()}]<span class=\"server\">SERVER: " + session["username"] + " has been banned."+"</span>", str(room_id))
        client_socket.emit("redirect")
        return
    elif "anything" not in session:
        session["anything"] = ""
        session["loginError"] = ""
        session["registerError"] = ""
        session["username"] = ""
        session["chat"] = ""
        session["room_id"] = ""
        client_socket.emit("redirect")
        return

    user_utils.status(session["username"], "Joined")
    seen = user_utils.get_account_info(session["username"])[3]

    if (datetime.now().minute - user_utils.convert_to_datetime(seen).minute) >= 10:
        user_utils.online(1, str(room_id))
    else:
        user_utils.online(1, str(room_id), silent=True)

    client_socket.emit(pong)


@ client_socket.on("disconnect")
def client_disconnected():
    global disconnect_detected
    client_socket.emit("clear tasks")
    print("\n\nCLIENT DISCONNECTED\n\n")
    client_socket.stop()
    disconnect_detected = True
    user_utils.monitor_activity(session["username"])


@ client_socket.on("connect")
def client_connect():
    print("\n\nCLIENT CONNECTED\n\n")


@client_socket.on("check disconnected")
def check_disconnected():
    global disconnect_detected

    if disconnect_detected:
        client_socket.emit("clear tasks")
        disconnect_detected = False


@ client_socket.on("create_room")
def createRoom(args):
    name = html.escape(args["name"])
    desc = html.escape(args["desc"])
    public = int(args["public"] == "Public")
    owner = args["owner"]

    owner_id = user_utils.get_account_info(owner)[4]
    new_room_id = base64.b64encode(str(secrets.randbits(128)).encode()).decode()

    ret = utils.repeat(
        event="append table",
        return_type=bool,
        data={
            "filename": "rooms",
            "folder": ".",
            "table": "Rooms",
            "columns": "Name, Description, ID, Public",
            "values": f"\"{name}\", \"{desc}\", \"{new_room_id}\", \"{public}\"",
            "unique": False
        }
    )

    returns = utils.repeat(
        event="create room",
        return_type=list,
        data={
            "name": name,
            "owner": owner,
            "owner_id": owner_id,
            "room_id": new_room_id
        }
    )

    return ret and all(r == True for r in returns)


@client_socket.on("get_rooms")
def get_rooms(data):
    pong = data["pong"]

    rooms = room_utils.get_rooms()
    section = ""

    for room in rooms:
        section += f"""
        <div class = \"chatroom-side\" >
            <a class=\"room-link\" onclick=\'move_room(\"{room[2]}\",\"{room[0]}\")\'>
                <p class = \"chatroom-title\" > {room[0]} </p> <i> 
                <p class = \"chatroom-description\">{room[1]}</p></i>
            </a>
        </div>"""

    client_socket.emit("recieve_rooms", {"rooms": section})
    client_socket.emit(pong)


@client_socket.on("new comment")
def get_new_comment(data):
    room_id = data["room_id"]
    message = data["message"]

    client_socket.emit("recieve_local_message", data)


def convert_to_html(message):
    msgSplit = ("".join(message.split("["))).split("]")
    msgTime = msgSplit[0]
    content = "".join(msgSplit[1:])

    newMessage = "<p class=\"msg-time\">"+msgTime+"</p><div class=\"bubble\"><div class=\"message\">"+content+"</div></div>"
    return newMessage


@client_socket.on("get_comments")
def get_comments(data):
    room_id = data["params"]
    pong = data["pong"]

    messages = room_utils.get_room_messages(room_id)
    newMessages = ""

    session["messages"] = messages

    for message in messages["messages"]:
        newMessages += convert_to_html(message)

    client_socket.emit("recieve_comments", {"messages": newMessages, "room_id": room_id}, broadcast=True)

    if session["chat"] != base64.b64encode(newMessages.encode()):
        session["chat"] = base64.b64encode(newMessages.encode())
        client_socket.emit("new_messages", {"room_id": room_id}, broadcast=True)

    client_socket.emit(pong)


@ client_socket.on("get_online")
def get_online(data):
    pong = data["pong"]

    client_socket.emit("recieve_online", {"online": user_utils.get_online()})
    client_socket.emit(pong)


@ app.route("/login", methods=["POST"])
def login():
    username = request.form["login-username"]
    password = hashlib.sha256(request.form["login-password"].encode()).hexdigest()

    data = {
        "filename": "accounts",
        "folder": "server",
        "table": "accounts",
        "select": "username, password",
        "where": f"username=\"{username}\" and password=\"{password}\""
    }

    # Check
    ret = utils.repeat(
        event="retrieve table",
        data=data,
        return_type=list
    )

    if ret:
        session["username"] = username

        user_utils.online(1, 0)
        chat_utils.autocolor()
        return redirect("/room/0")

    session["loginError"] = "Invalid Username or Password"
    return redirect("/")


@ app.route("/register", methods=["POST"])
def register():
    if gateway():
        return render_template("banned.html")

    username = request.form["register-username"]
    password = hashlib.sha256(request.form["register-password"].encode()).hexdigest()
    check_password = hashlib.sha256(request.form["register-password-again"].encode()).hexdigest()

    f = open("./info/accounts.json", "a+")
    f.seek(0)
    accounts = json.load(f)

    if username in accounts:
        session["registerError"] = "Username already exists."
        f.close()
        return redirect("/")
    elif password != check_password:
        session["registerError"] = "Password did not match, please try again."
        f.close()
        return redirect("/")

    accounts[username] = {"password": password, "ip": request.environ.get("REMOTE_ADDR")}
    app.logger.info(f"[{accounts[username]['ip']}]: Created account {username}.")

    user_utils.online(1, 0)

    session["username"] = username
    chat_utils.autocolor()
    return redirect("/room/0")


@ app.route("/room/<room_id>")
def chat(room_id):
    if gateway():
        return render_template("banned.html")

    if "username" not in session:
        return redirect("/")
    elif session["username"] == "":
        return redirect("/")

    room_name = room_utils.get_room_name(room_id)
    room_admin = session["username"] in room_utils.get_room_info(room_id, "Admins", where=f"Username=\'{session['username']}\'")

    user_id = user_utils.get_account_info(session["username"])[4]

    return render_template("chat.html",
                           room_id=str(room_id),
                           room_name=room_name,
                           username=session["username"],
                           room_admin=room_admin,
                           user_id=user_id)


@ client_socket.on("send")
def send(message, room_id, author_id):
    if message == "\n" or message[0] == " ":
        return

    print("\n\nNEW MESSAGE\n\n")

    user = session["special"]
    msg = f"[{time.asctime()}]{user}: "+html.escape(message)
    utils.repeat(
        event="append message",
        return_type=bool,
        data={
            "room_id": room_id,
            "author_id": author_id,
            "author_ip": request.remote_addr,
            "message": msg
        }
    )

    data = {
        "room_id": room_id,
        "message": convert_to_html(msg)
    }
    client_socket.emit("recieve_local_message", data, broadcast=True, include_self=True)
    client_socket.emit("new_messages", data, broadcast=True, include_self=True)


def gateway():
    ip = request.remote_addr

    data = {
        "filename": "blacklist",
        "folder": "server",
        "table": "blacklist",
        "select": "ip",
        "where": f"ip=\"{ip}\""
    }

    is_blacklisted = utils.repeat(
        function=rss.rss_socket.emit,
        event="retrieve table",
        data=data,
        return_type=list
    )

    blacklisted_users = [user[0] for user in is_blacklisted]

    if ip in blacklisted_users:
        return True

    return False


def disconnect():
    rss.disconnect()


if __name__ == "__main__":
    rss.disconnect()
    rss.connect()

    atexit.register(disconnect)
    user_utils.clear_online()
    print("Started server.")

    client_socket.run(app, host=HOST, port=PORT, debug=app.config["DEBUG"], use_reloader=True)
    print("Exiting Server...")
    client_socket.stop()
    rss.disconnect()
