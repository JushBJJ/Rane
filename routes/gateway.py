from create_app import app
from flask import request
from utils import utils


def gateway() -> bool:
    """Check whether the user is banned or not."""
    ip = request.remote_addr

    data = {
        "filename": "blacklist",
        "folder": "server",
        "table": "blacklist",
        "select": "ip",
        "where": f"ip=\"{ip}\""
    }

    is_blacklisted = utils.call_db(
        event="retrieve table",
        data=data,
        return_type=list
    )

    blacklisted_users = [user[0] for user in is_blacklisted]

    if ip in blacklisted_users:
        return True

    return False
