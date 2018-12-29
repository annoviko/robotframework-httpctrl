import threading

from copy import copy
from robot.api import logger


class ResponseStorage:
    __response = None
    __response_condition = threading.Condition()

    @staticmethod
    def __ready():
        return ResponseStorage.__response is not None

    @staticmethod
    def push(response):
        with ResponseStorage.__response_condition:
            logger.info("Push response to the Response Storage: %s" % response)
            ResponseStorage.__response = response
            ResponseStorage.__response_condition.notify()

    @staticmethod
    def pop(timeout=5.0):
        with ResponseStorage.__response_condition:
            if ResponseStorage.__response is None:
                result = ResponseStorage.__response_condition.wait_for(ResponseStorage.__ready, timeout)
                if result is True:
                    logger.info("Pop response from the Response Storage: %s" % ResponseStorage.__response)
                else:
                    logger.info("Timeout - no response is obtained from Response Storage.")

            response = copy(ResponseStorage.__response)
            ResponseStorage.__response = None

        return response
