"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""

from http.server import SimpleHTTPRequestHandler
from robot.api import logger

from HttpCtrl.internal_messages import TerminationRequest, IgnoreRequest
from HttpCtrl.request import Request
from HttpCtrl.request_storage import RequestStorage
from HttpCtrl.response_storage import ResponseStorage
from HttpCtrl.http_stub import HttpStubContainer, HttpStubCriteria


class HttpHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.server_version = "HttpCtrl.Server/"
        self.sys_version = ""

        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)


    def do_GET(self):
        self.__default_handler('GET')


    def do_POST(self):
        self.__default_handler('POST')


    def do_PUT(self):
        self.__default_handler('PUT')


    def do_OPTIONS(self):
        self.__default_handler('OPTIONS')


    def do_HEAD(self):
        self.__default_handler('HEAD')


    def do_PATCH(self):
        self.__default_handler('PATCH')


    def do_DELETE(self):
        self.__default_handler('DELETE')


    def log_message(self, format, *args):
        return


    def log_error(self, format, *args):
        return


    def log_request(self, code='-', size='-'):
        return


    def __extract_body(self):
        body_length = int(self.headers.get('Content-Length', 0))
        if body_length > 0:
            return self.rfile.read(body_length)

        return None


    def __default_handler(self, method):
        host, port = self.client_address[:2]
        body = self.__extract_body()

        logger.info("'%s' request is received from '%s:%s'." % (method, host, port))

        stub = HttpStubContainer().get(HttpStubCriteria(method=method, url=self.path))
        if stub is not None:
            response = stub.response

        else:
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

        self.send_response(response.get_status())

        headers = response.get_headers()
        if headers is not None:
            for key, value in headers.items():
                self.send_header(key, value)

        body = response.get_body()
        if body is not None:
            if isinstance(response.get_body(), str):
                body = response.get_body().encode("utf-8")

            self.send_header('Content-Length', str(len(body)))

        self.end_headers()

        if body is not None:
            self.wfile.write(body)
