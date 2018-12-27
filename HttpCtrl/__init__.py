import http.client
import json
import threading
import time

from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer


class Client:
    def __init__(self):
        self.__host = None
        self.__port = None

        self.__request_headers = {}

        self.__response_status = None
        self.__response_body = None


    def initialize_client(self, host, port):
        self.__host = host
        self.__port = port


    def __send_request(self, connection_type, method, url, body):
        if self.__host is None or self.__port is None:
            raise AssertionError("Client is not initialized (host and port are empty).")

        endpoint = "%s:%s" % (self.__host, str(self.__port))

        if connection_type == 'http':
            connection = http.client.HTTPConnection(endpoint)
        elif connection_type == 'https':
            connection = http.client.HTTPSConnection(endpoint)
        else:
            raise AssertionError("Internal error of the client, please report to "
                                 "'https://github.com/annoviko/robotframework-httpctrl/issues'.")

        connection.request(method, url, body, self.__request_headers)

        print("*INFO:%d* Request (type: '%s', method '%s') is sent to %s." %
              (time.time() * 1000, connection_type, method, endpoint))

        if body is not None:
            print("*INFO:%d* Request body: %s" % (time.time() * 1000, body))

        response = connection.getresponse()
        self.__response_status = response.status
        self.__response_body = response.read().decode('utf-8')

        connection.close()


    def send_http_request(self, method, url, body=None):
        self.__send_request('http', method, url, body)


    def send_https_request(self, method, url, body=None):
        self.__send_request('https', method, url, body)


    def set_request_header(self, key, value):
        self.__request_headers[key] = value


    def get_response_status(self):
        return self.__response_status


    def get_response_body(self):
        return self.__response_body


    def get_json_value(self, json_string, path):
        json_content = json.loads(json_string)
        keys = path.split('/')

        current_element = json_content
        for key in keys:
            current_element = current_element[key]

        return current_element



class IncomingRequest:
    def __init__(self, host, port, method, url, body=None):
        self.__endpoint = (host, port)
        self.__method = method
        self.__url = url
        self.__body = body

    def get_endpoint(self):
        return self.__endpoint

    def get_method(self):
        return self.__method

    def get_url(self):
        return self.__url

    def get_body(self):
        return self.__body



class RequestStorage:
    __request = None
    __request_condition = threading.Condition()

    @staticmethod
    def push(request):
        RequestStorage.__request_condition.acquire()
        RequestStorage.__request = request
        RequestStorage.__request_condition.release()

        RequestStorage.__request_condition.notify()

    @staticmethod
    def pop(timeout=5.0):
        RequestStorage.__request_condition.acquire()

        if RequestStorage.__request is None:
            RequestStorage.__request_condition.wait(timeout)

        response = RequestStorage.__request
        RequestStorage.__request = None
        RequestStorage.__request_condition.release()

        return response


class OutgoingResponse:
    def __init__(self, status, body, headers):
        self.__status = status
        self.__body = body
        self.__headers = headers

    def get_status(self):
        return self.__status

    def get_body(self):
        return self.__body

    def get_headers(self):
        return self.__headers



class ResponseStorage:
    __response = None
    __response_condition = threading.Condition()

    @staticmethod
    def push(response):
        ResponseStorage.__response_condition.acquire()
        ResponseStorage.__response = response
        ResponseStorage.__response_condition.release()

        ResponseStorage.__response_condition.notify()


    @staticmethod
    def pop(timeout=5.0):
        ResponseStorage.__response_condition.acquire()

        if ResponseStorage.__response is None:
            ResponseStorage.__response_condition.wait(timeout)

        response = ResponseStorage.__response
        ResponseStorage.__response = None
        ResponseStorage.__response_condition.release()

        return response



class HttpHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.server_version = "HttpCtrlServer/"
        self.sys_version = ""

        self.__incoming_condition = threading.Condition()
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)


    def do_GET(self):
        host, port = self.client_address[:2]
        request = IncomingRequest(host, port, 'GET', self.path)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def do_POST(self):
        host, port = self.client_address[:2]
        body = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        request = IncomingRequest(host, port, 'POST', self.path, body)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def do_DELETE(self):
        host, port = self.client_address[:2]
        request = IncomingRequest(host, port, 'DELETE', self.path)
        RequestStorage.push(request)

        response = ResponseStorage.pop()
        self.__send_response(response)


    def __send_response(self, response):
        if response is None:
            raise AssertionError("Response is not provided for incoming request.")

        self.send_response(response.get_status(), response.get_body())

        headers = response.get_headers()
        for key, value in headers.items():
            self.send_header(key, value)

        body = None
        if response.body is not None:
            body = response.body.encode("utf-8")
            self.send_header('Content-Length', len(body))

        self.end_headers()

        if body is not None:
            self.wfile.write(body)



class HttpServer:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

        self.__handler = None
        self.__server = None


    def __del__(self):
        self.__server.shutdown()
        self.__server.server_close()


    def start(self):
        self.__handler = HttpHandler
        self.__server = TCPServer((self.__host, self.__port), self.__handler)

        try:
            self.__server.serve_forever()
        except Exception as exception:
            print("*INFO:%d* Stop HTTP server because of exception." % time.time())
            self.stop()

            raise exception


    def stop(self):
        self.__server.shutdown()
        self.__server.server_close()

        print("*INFO:%d* HTTP server is successfully stopped." % time.time())



class Server:
    def __init__(self):
        self.__response_headers = {}
        self.__request = None

        self.__server = None
        self.__thread = None


    def start_server(self, host, port):
        self.__server = HttpServer(host, port)
        self.__thread = threading.Thread(target=self.__server.start)
        self.__thread.start()


    def stop_server(self):
        if self.__server is None:
            raise AssertionError("Impossible to stop server because it has not been started.")

        self.__server.stop()
        self.__thread.join()


    def wait_for_request(self):
        self.__request = RequestStorage.pop()
        if self.__request is None:
            raise AssertionError("Timeout: request was not received.")

        # TODO: print request


    def get_request_method(self):
        return self.__request.get_method()


    def set_reply_header(self, key, value):
        self.__response_headers[key] = value


    def reply_by(self, status, body):
        response = OutgoingResponse(status, body, self.__response_headers)
        ResponseStorage.push(response)

        self.__response_headers.clear()