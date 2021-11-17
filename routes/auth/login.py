from flask import request, session, jsonify
from utils import utils, user_utils, chat_utils

import hashlib
import bcrypt


def login():
    """Login user."""
    username = request.form["username"]
    password = hashlib.sha256(request.form["password"].encode()).hexdigest()

    data = {
        "filename": "accounts",
        "folder": "server",
        "table": "accounts",
        "select": "username, password",
        "where": "username = '{}'".format(username)
    }

    # Check if user exists.
    ret = utils.call_db(
        event="retrieve table",
        data=data,
        return_type=list
    )

    if ret:
        # Check if password is correct.
        if bcrypt.checkpw(password.encode(), ret[0][1].encode()):
            session["username"] = username

            user_utils.online(1, 0)
            chat_utils.autocolor("0")
            return jsonify({"url": "/room/0"})

    session["login_error"] = "Invalid Username or Password"
    return jsonify({"url": "/"})
