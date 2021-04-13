import threading
import server
import resources.resource_server as resource_server

import time


class RSSServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting RSS Server")
        resource_server.main()
        print("Stopped RSS Server")


class WebsiteServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting Website Server")
        server.main()
        print("Stopped Website Server")


if __name__ == "__main__":
    RSS = RSSServer()
    Website = WebsiteServer()

    RSS.start()
    time.sleep(3)

    Website.start()

    RSS.join()
    Website.join()
