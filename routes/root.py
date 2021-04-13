from flask import request, session, render_template

import routes.gateway as routes
import create_app


app = create_app.app


def root():
    if routes.gateway() == True:
        app.logger.info(f"{request.remote_addr} connected to enter the server.")
        return render_template("banned.html")

    session["anything"] = ""
    session["login_error"] = ""
    session["register_error"] = ""
    session["username"] = ""
    session["chat"] = ""
    session["room_id"] = 0

    return render_template("login.html",
                           login_error=session["login_error"],
                           register_error=session["register_error"])
