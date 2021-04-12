from utils import rss
from utils import room_utils

import pytest
import time


@pytest.mark.timeout(10)
def test_get_room_name():
    rss.connect()
    ret = room_utils.get_room_name("0")
    rss.disconnect()
    assert ret == "Genesis"


@pytest.mark.timeout(10)
def test_get_room_info():
    rss.connect()
    ret = room_utils.get_room_info("0", table="Messages", select="message")
    rss.disconnect()
    assert type(ret) == list


@pytest.mark.timeout(10)
def test_list_rooms():
    ret = room_utils.list_rooms()
    assert ret[0] == "0.db"


@pytest.mark.timeout(60)
def test_set_room_info():
    rss.connect()
    ret = room_utils.set_room_info("0", table="test", where="Test=\"test\"", value="Test=\"test\"")
    rss.disconnect()
    assert ret == True


@pytest.mark.timeout(60)
def test_get_room_messages():
    rss.connect()
    ret = room_utils.get_room_messages("0")
    rss.disconnect()
    assert type(ret) == dict


@pytest.mark.timeout(60)
def test_get_rooms():
    rss.connect()
    ret = room_utils.get_rooms()
    rss.disconnect()
    assert type(ret) == list
