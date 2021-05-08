from utils import utils, rss
from flask import request


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
        function=rss.rss_socket.emit,
        event="retrieve table",
        data=data,
        return_type=list
    )

    blacklisted_users = [user[0] for user in is_blacklisted]

    if ip in blacklisted_users:
        return True

    return False
