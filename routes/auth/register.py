from utils import utils, user_utils, chat_utils
from flask import request, session, redirect, jsonify
from resources import db

import hashlib
import bcrypt


def check_password_requirements(password: str) -> str:
    """Check if password meets requirements."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."
    return ""


def hash_password(password: str) -> str:
    """Hash and salt password."""
    hashed = hashlib.sha256(password.encode()).hexdigest()
    salted = bcrypt.hashpw(hashed.encode(), bcrypt.gensalt())
    return salted.decode()


def register():
    """Register user."""
    username = request.form["username"]
    password = request.form["password"]
    confirm_password = request.form["password-again"]
    ip = request.remote_addr

    session["register_error"] = check_password_requirements(password)

    if not password == confirm_password:
        session["register_error"] = "Password and confirmation password do not match."
        return jsonify({"url": "/"})
    elif session["register_error"]:
        return jsonify({"url": "/"})

    password = hash_password(password)
    confirm_password = hash_password(confirm_password)  # This may be redundant

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

        user_id = db.get_id_by_user({"username": username})
        utils.call_db(event="join room", data={"room_id": "0", "user_id": user_id}, return_type=bool)

        user_utils.online(1, 0)
        chat_utils.autocolor("0")
        return jsonify({"url": "/room/0"})

    session["register_error"] = "Username already taken."
    return jsonify({"url": "/"})
