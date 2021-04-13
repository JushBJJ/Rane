from flask import request
from utils import utils, rss


def gateway():
    ip = request.remote_addr

    data = {
        "filename": "blacklist",
        "folder": "server",
        "table": "blacklist",
        "select": "ip",
        "where": f"ip=\"{ip}\""
    }

    is_blacklisted = utils.repeat(
        function=rss.rss_socket.emit,
        event="retrieve table",
        data=data,
        return_type=list
    )

    blacklisted_users = [user[0] for user in is_blacklisted]

    if ip in blacklisted_users:
        return True

    return False
