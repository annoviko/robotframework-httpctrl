"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2019
Copyright: GNU Public License

HttpCtrl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

HttpCtrl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

class Request:
    def __init__(self, host, port, method, url, headers, body=None):
        self.__endpoint = (host, port)
        self.__method = method
        self.__url = url
        self.__body = body
        self.__headers = headers

    def __copy__(self):
        return Request(self.__endpoint[0], self.__endpoint[1], self.__method, self.__url, self.__headers, self.__body)

    def __str__(self):
        return "%s %s\n%s" % (self.__method, self.__url, self.__body)

    def get_endpoint(self):
        return self.__endpoint

    def get_method(self):
        return self.__method

    def get_headers(self):
        return self.__headers

    def get_url(self):
        return self.__url

    def get_body(self):
        return self.__body
