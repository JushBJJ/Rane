from flask import session, redirect, render_template
from utils import room_utils, user_utils
from typing import Any

import routes.gateway as routes


def room(room_id: str) -> Any:
    """Room page."""
    if routes.gateway():
        return render_template("banned.html")

    # Redirect if session is not defined.
    if "username" not in session:
        return redirect("/")
    elif session["username"] == "":
        return redirect("/")

    room_admins = dict(room_utils.get_room_info(room_id, "Admins", select="Username"))

    # Set jinja values.
    room_name = room_utils.get_room_name(room_id)
    is_admin = session["username"] in list(room_admins.keys())
    user_id = user_utils.get_account_info(session["username"])[4]

    return render_template("chat.html",
                           room_id=str(room_id),
                           room_name=room_name,
                           username=session["username"],
                           room_admin=is_admin,
                           user_id=user_id)
