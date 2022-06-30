"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""

from threading import Lock

from HttpCtrl.utils.singleton import Singleton


class HttpStubCriteria:
    def __init__(self, **kwargs):
        self.method = kwargs.get('method', None)
        if self.method is not None:
            self.method = self.method.upper()

        self.url = kwargs.get('url', None)
        if self.url is not None:
            self.url = self.url.lower()


    def __eq__(self, other):
        return (self.method == other.method) and (self.url == other.url)


class HttpStub:
    def __init__(self, criteria, response):
        self.criteria = criteria
        self.response = response
        self.count = 0


class HttpStubContainer(metaclass=Singleton):
    def __init__(self):
        self.__stubs = []
        self.__lock = Lock()


    def add(self, criteria, response):
        with self.__lock:
            self.__stubs.append(HttpStub(criteria, response))


    def count(self, criteria):
        with self.__lock:
            for stub in self.__stubs:
                if self.__is_satisfy(stub, criteria) is True:
                    return stub.count
            
            return 0


    def get(self, criteria):
        with self.__lock:
            for stub in self.__stubs:
                if self.__is_satisfy(stub, criteria) is True:
                    stub.count += 1
                    return stub
        
            return None


    def clear(self):
        with self.__lock:
            self.__stubs.clear()


    def __is_satisfy(self, stub, criteria):
        if stub.criteria == criteria:
            return True
        
        return False
        