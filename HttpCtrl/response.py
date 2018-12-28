class Response:
    def __init__(self, status, body, headers):
        self.__status = status
        self.__body = body
        self.__headers = headers

    def __str__(self):
        if self.__body is None or len(self.__body) == 0:
            return str(self.__status)

        return "%s\n%s" % (str(self.__status), self.__body)

    def get_status(self):
        return self.__status

    def get_body(self):
        return self.__body

    def get_headers(self):
        return self.__headers
