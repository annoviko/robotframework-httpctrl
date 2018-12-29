class Request:
    def __init__(self, host, port, method, url, body=None):
        self.__endpoint = (host, port)
        self.__method = method
        self.__url = url
        self.__body = body

    def __copy__(self):
        return Request(self.__endpoint[0], self.__endpoint[1], self.__method, self.__url, self.__body)

    def __str__(self):
        return "%s %s\n%s" % (self.__method, self.__url, self.__body)

    def get_endpoint(self):
        return self.__endpoint

    def get_method(self):
        return self.__method

    def get_url(self):
        return self.__url

    def get_body(self):
        return self.__body
