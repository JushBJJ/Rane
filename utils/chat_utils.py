from utils.utils import get_session
from utils import user_utils


def autocolor(room_id: str, testing: bool = False) -> str:
    """Insert role color into a user's username."""
    # TODO room specific autocolor
    session = get_session()

    if testing:
        room_id = "0"
        session = {"username": "Jush"}

    username = session["username"]

    # Set Rane Role
    role = user_utils.get_account_server_role(username)
    role_class = role.replace(" ", "_").lower()

    if role_class != "":
        span = f"<span class=\'{role_class}\'>{role}</span>"
        username += " &lbrack;"+span+"&rbrack;"

    # Set Room Role
    role = user_utils.get_account_room_role(session["username"], room_id)
    role_class = role.replace(" ", "_").lower()

    span = f"<span class=\'{role_class}\'>{role}</span>"
    username += " ("+span+")"

    session["special"] = username
    return session["special"]
