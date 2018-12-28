import threading


class RequestStorage:
    __request = None
    __request_condition = threading.Condition()

    @staticmethod
    def __ready():
        return RequestStorage.__request is not None

    @staticmethod
    def push(request):
        with RequestStorage.__request_condition:
            RequestStorage.__request = request
            RequestStorage.__request_condition.notify()

    @staticmethod
    def pop(timeout=5.0):
        with RequestStorage.__request_condition:
            if RequestStorage.__request is None:
                RequestStorage.__request_condition.wait_for(RequestStorage.__ready, timeout)

            response = RequestStorage.__request
            RequestStorage.__request = None

        return response
