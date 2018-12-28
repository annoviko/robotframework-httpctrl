import threading
import time


from HttpCtrl.logger import Logger


class ResponseStorage:
    __response = None
    __response_condition = threading.Condition()

    @staticmethod
    def __ready():
        return ResponseStorage.__response is not None

    @staticmethod
    def push(response):
        with ResponseStorage.__response_condition:
            ResponseStorage.__response = response
            ResponseStorage.__response_condition.notify()

    @staticmethod
    def pop(timeout=5.0):
        with ResponseStorage.__response_condition:
            if ResponseStorage.__response is None:
                ResponseStorage.__response_condition.wait_for(ResponseStorage.empty, timeout)

            response = ResponseStorage.__response
            ResponseStorage.__response = None

        return response
