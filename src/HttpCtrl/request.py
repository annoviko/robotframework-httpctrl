"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""


from HttpCtrl.utils.logger import LoggerAssistant


class Request:
    def __init__(self, host, port, method, url, headers, body=None):
        self.__source_host = host
        self.__source_port = port
        self.__method = method
        self.__url = url
        self.__body = body
        self.__headers = headers

    def __copy__(self):
        return Request(self.__source_host, self.__source_port, self.__method, self.__url, self.__headers, self.__body)

    def __str__(self):
        body_to_log = LoggerAssistant.get_body(self.__body)
        return "%s %s\n%s" % (self.__method, self.__url, body_to_log)

    def get_source_address(self):
        return self.__source_host

    def get_source_port(self):
        return self.__source_port

    def get_method(self):
        return self.__method

    def get_headers(self):
        return self.__headers

    def get_url(self):
        return self.__url

    def get_body(self):
        return self.__body
