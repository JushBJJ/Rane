from typing import Text
from flask import render_template


def maintenance() -> Text:
    """Maintenance age."""
    return render_template("maintenance.html")
