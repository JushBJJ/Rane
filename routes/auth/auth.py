from flask_restful import Resource
from flask_restful import reqparse, Resource
from utils import utils, rss

parser = reqparse.RequestParser()


class authorize(Resource):
    def post(self):
        """Authorize user if username and password match."""
        parser.add_argument("username")
        parser.add_argument("password")

        args = parser.parse_args()
        username = args["username"]
        password = args["password"]

        data = {
            "filename": "accounts",
            "folder": "server",
            "table": "accounts",
            "select": "username, password",
            "where": f"username=\"{username}\" and password=\"{password}\""
        }

        # Check
        ret = utils.repeat(
            event="retrieve table",
            data=data,
            return_type=list
        )
        return ret
