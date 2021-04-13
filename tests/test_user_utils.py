from utils import rss, user_utils, utils
import time


def test_status():
    rss.connect()
    ret = user_utils.status("Jush", "Left")
    rss.disconnect()
    assert ret == True


def test_get_online():
    rss.connect()
    ret = user_utils.get_online()
    rss.disconnect()
    assert type(ret) == int


def test_online():
    rss.connect()

    ret1 = user_utils.online(1, 0, testing=True)
    ret2 = user_utils.online(-1, 0, testing=True)

    rss.disconnect()
    assert (ret1 == True and ret2 == True) == True


def test_clear_online():
    rss.connect()
    ret = user_utils.clear_online()
    rss.disconnect()

    assert ret == True


def test_get_account_info():
    rss.connect()
    ret = user_utils.get_account_info("Jush")
    rss.disconnect()

    assert type(ret) == list

# TODO Create test for monitor activity
