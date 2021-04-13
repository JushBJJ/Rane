from typing import Text
from flask import render_template


def maintenance() -> Text:
    return render_template("maintenance.html")
