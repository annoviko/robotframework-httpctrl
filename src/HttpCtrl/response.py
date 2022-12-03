"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""


from HttpCtrl.utils.logger import LoggerAssistant


class Response:
    def __init__(self, status, reason, body, body_file, headers : dict):
        self.__status = status
        self.__reason = reason
        self.__body = body
        self.__body_file = body_file
        self.__headers = headers

    def __str__(self):
        if (self.__body is None) or (len(self.__body) == 0):
            if self.__body_file is None:
                return str(self.__status)
            else:
                return "%s\n<body is in the file: '%s'>" % (self.__status, self.__body_file)

        body_to_log = LoggerAssistant.get_body(self.__body)
        return "%s\n%s" % (str(self.__status), body_to_log)

    def __copy__(self):
        return Response(self.__status, self.__reason, self.__body, self.__body_file, self.__headers)

    def get_status(self):
        return self.__status

    def get_reason(self):
        return self.__reason

    def get_body_file(self):
        return self.__body_file

    def get_body(self):
        if (self.__body is None) and (self.__body_file is not None):
            with open(self.__body_file) as file_stream:
                return file_stream.read()
        
        return self.__body

    def get_headers(self) -> dict:
        return self.__headers
