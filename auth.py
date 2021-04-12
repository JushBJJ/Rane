from flask_restful import Resource
from flask_restful import reqparse, Resource
from utils import utils, rss

parser = reqparse.RequestParser()


class authorize(Resource):
    def post(self):
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

        print("BRUH")

        # Check
        ret = utils.repeat(
            event="retrieve table",
            data=data,
            return_type=list
        )

        print(ret)

        return ret
