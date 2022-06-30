"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""

import threading

from robot.api import logger

from HttpCtrl.utils.singleton import Singleton


class RequestStorage(metaclass=Singleton):
    def __init__(self):
        self.__request = None
        self.__event_incoming = threading.Condition()


    def __ready(self):
        return self.__request is not None


    def push(self, request):
        with self.__event_incoming:
            logger.info("Push request to the Request Storage: %s" % request)
            self.__request = request
            self.__event_incoming.notify()


    def pop(self, timeout=5.0):
        with self.__event_incoming:
            if not self.__ready():
                result = self.__event_incoming.wait_for(self.__ready, timeout)
                if result is False:
                    return None

            request = self.__request
            self.__request = None
            return request


    def clear(self):
        with self.__event_incoming:
            self.__request = None
