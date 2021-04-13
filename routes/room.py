from flask import session, redirect, render_template
from utils import room_utils, user_utils

import routes.gateway as routes


def room(room_id):
    if routes.gateway():
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
