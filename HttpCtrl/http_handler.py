import threading

from http.server import SimpleHTTPRequestHandler

from HttpCtrl.logger import Logger
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

        Logger.info("'GET' request is received from '%s:%s'." % (host, port))

        request = Request(host, port, 'GET', self.path)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def do_POST(self):
        host, port = self.client_address[:2]

        Logger.info("'POST' request is received from '%s:%s'." % (host, port))

        body = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        request = Request(host, port, 'POST', self.path, body)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        print("Response is following:", response)
        self.__send_response(response)


    def do_DELETE(self):
        host, port = self.client_address[:2]

        Logger.info("'DELETE' request is received from '%s:%s'." % (host, port))

        request = Request(host, port, 'DELETE', self.path)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def __send_response(self, response):
        print("Response is following:", response)
        if response is None:
            Logger.error("Response is not provided for incoming request.")
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

        Logger.info("HTTP response is successfully sent.")
