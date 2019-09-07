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

from http.server import SimpleHTTPRequestHandler
from robot.api import logger

from HttpCtrl.internal_messages import TerminationRequest, IgnoreRequest
from HttpCtrl.request import Request
from HttpCtrl.request_storage import RequestStorage
from HttpCtrl.response_storage import ResponseStorage


class HttpHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.server_version = "HttpCtrl.Server/"
        self.sys_version = ""

        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)


    def do_GET(self):
        self.__default_handler('GET')


    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        self.__default_handler('POST', body)


    def do_PUT(self):
        body = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        self.__default_handler('PUT', body)


    def do_OPTIONS(self):
        self.__default_handler('OPTIONS')


    def do_HEAD(self):
        self.__default_handler('HEAD')


    def do_PATCH(self):
        body = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        self.__default_handler('PATCH', body)


    def do_DELETE(self):
        self.__default_handler('DELETE')


    def log_message(self, format, *args):
        return


    def log_error(self, format, *args):
        return


    def log_request(self, code='-', size='-'):
        return


    def __default_handler(self, method, body=None):
        host, port = self.client_address[:2]

        logger.info("'%s' request is received from '%s:%s'." % (method, host, port))

        request = Request(host, port, method, self.path, self.headers, body)
        RequestStorage().push(request)

        response = ResponseStorage().pop()
        if isinstance(response, TerminationRequest) or isinstance(response, IgnoreRequest):
            return

        try:
            self.__send_response(response)
        except Exception as exception:
            logger.info("Response was not sent to client due to reason: '%s'." % str(exception))


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
