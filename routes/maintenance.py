from flask import render_template
from typing import Text


def maintenance() -> Text:
    """Maintenance age."""
    return render_template("maintenance.html")
