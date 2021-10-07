"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2021
Copyright: The 3-Clause BSD License

"""

class Response:
    def __init__(self, status, reason, body, headers):
        self.__status = status
        self.__reason = reason
        self.__body = body
        self.__headers = headers

    def __str__(self):
        if self.__body is None or len(self.__body) == 0:
            return str(self.__status)

        return "%s\n%s" % (str(self.__status), self.__body)

    def __copy__(self):
        return Response(self.__status, self.__reason, self.__body, self.__headers)

    def get_status(self):
        return self.__status

    def get_reason(self):
        return self.__reason

    def get_body(self):
        return self.__body

    def get_headers(self):
        return self.__headers
