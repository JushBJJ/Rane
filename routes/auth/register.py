from utils import utils, user_utils, chat_utils
from flask import request, session, redirect

import hashlib


def register():
    """Register user."""
    username = request.form["register-username"]
    password = hashlib.sha256(request.form["register-password"].encode()).hexdigest()
    confirm_password = hashlib.sha256(request.form["register-password-again"].encode()).hexdigest()
    ip = request.remote_addr

    if not password == confirm_password:
        session["register_error"] = "Password and confirmation password do not match."
        return redirect("/")

    data = {
        "filename": "accounts",
        "folder": "server",
        "table": "accounts",
        "select": "username",
        "where": f"username=\"{username}\""
    }

    # Check if user already exists
    ret = utils.call_db(
        event="retrieve table",
        data=data,
        return_type=list
    )

    if not ret:
        # Add user to database.
        utils.call_db(
            event="append table",
            data={
                "filename": "accounts",
                "folder": "server",
                "table": "accounts",
                "columns": "username, password, ip",
                "values": f"\"{username}\", \"{password}\", \"{ip}\"",
                "unique": False
            },
            return_type=bool
        )
        session["username"] = username

        user_utils.online(1, 0)
        chat_utils.autocolor("0")
        return redirect("/room/0")

    session["register_error"] = "Username already taken."
    return redirect("/")
