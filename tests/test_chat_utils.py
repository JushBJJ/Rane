from utils import rss
from utils import chat_utils

import time


def test_autocolor():
    rss.connect()
    ret = chat_utils.autocolor(testing=True)
    rss.disconnect()
    assert ret == "Jush(<span class=\"admin\">ADMIN</span>)"
