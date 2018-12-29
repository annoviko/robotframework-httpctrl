import threading

from copy import copy
from robot.api import logger


class RequestStorage:
    __request = None
    __request_condition = threading.Condition()

    @staticmethod
    def __ready():
        return RequestStorage.__request is not None

    @staticmethod
    def push(request):
        with RequestStorage.__request_condition:
            logger.info("Push request to the Request Storage: %s" % request)
            RequestStorage.__request = request
            RequestStorage.__request_condition.notify()

    @staticmethod
    def pop(timeout=5.0):
        with RequestStorage.__request_condition:
            if RequestStorage.__request is None:
                result = RequestStorage.__request_condition.wait_for(RequestStorage.__ready, timeout)
                if result is True:
                    logger.info("Pop request from the Request Storage: %s" % RequestStorage.__request)
                else:
                    logger.info("Timeout - no request is obtained from Request Storage.")

            request = copy(RequestStorage.__request)
            RequestStorage.__request = None

        return request
