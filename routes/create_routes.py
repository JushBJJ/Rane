from routes.maintenance import maintenance
from routes.auth.register import register
from routes.auth.login import login
from routes.root import root
from routes.room import room

import create_app


def create_routes() -> None:
    """Create all page routes of the website."""
    app = create_app.app

    # Main Pages
    app.add_url_rule("/", "root", root)
    app.add_url_rule("/room/<room_id>", "room", room, defaults={"room_id": 0})
    app.add_url_rule("/maintenance", "maintenance", maintenance)

    # Auth
    app.add_url_rule("/login", "login", login, methods=["POST"])
    app.add_url_rule("/register", "register", register, methods=["POST"])
