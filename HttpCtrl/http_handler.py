"""!

@brief HTTP server request handler.

@authors Andrei Novikov (pyclustering@yandex.ru)
@date 2018-2019
@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyClustering is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyClustering is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond

"""

import threading

from http.server import SimpleHTTPRequestHandler
from robot.api import logger

from HttpCtrl.request import Request
from HttpCtrl.request_storage import RequestStorage
from HttpCtrl.response_storage import ResponseStorage


class HttpHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.server_version = "HttpCtrlServer/"
        self.sys_version = ""

        self.__incoming_condition = threading.Condition()
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)


    def do_GET(self):
        host, port = self.client_address[:2]

        logger.info("'GET' request is received from '%s:%s'." % (host, port))

        request = Request(host, port, 'GET', self.path, self.headers)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def do_POST(self):
        host, port = self.client_address[:2]

        logger.info("'POST' request is received from '%s:%s'." % (host, port))

        body = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        request = Request(host, port, 'POST', self.path, self.headers, body)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def do_DELETE(self):
        host, port = self.client_address[:2]

        logger.info("'DELETE' request is received from '%s:%s'." % (host, port))

        request = Request(host, port, 'DELETE', self.path, self.headers)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def log_message(self, format, *args):
        return


    def log_error(self, format, *args):
        return


    def log_request(self, code='-', size='-'):
        return


    def __send_response(self, response):
        if response is None:
            logger.error("Response is not provided for incoming request.")
            return

        self.send_response(response.get_status(), response.get_body())

        headers = response.get_headers()
        for key, value in headers.items():
            self.send_header(key, value)

        body = None
        if response.get_body() is not None:
            body = response.get_body().encode("utf-8")
            self.send_header('Content-Length', len(body))

        self.end_headers()

        if body is not None:
            self.wfile.write(body)
