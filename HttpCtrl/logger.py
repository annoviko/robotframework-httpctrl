import threading
import time


class Logger:
    __resource_locker = threading.RLock()

    @staticmethod
    def info(message):
        with Logger.__resource_locker:
            print("*INFO:%d* %s" % (time.time() * 1000, message))


    @staticmethod
    def error(message):
        with Logger.__resource_locker:
            print("*ERROR:%d* %s" % (time.time() * 1000, message))
