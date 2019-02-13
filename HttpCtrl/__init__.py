import http.client
import json
import threading

from robot.api import logger

from HttpCtrl.http_server import HttpServer
from HttpCtrl.request import Request
from HttpCtrl.request_storage import RequestStorage
from HttpCtrl.response_storage import ResponseStorage
from HttpCtrl.response import Response


class Client:
    def __init__(self):
        self.__host = None
        self.__port = None

        self.__request_headers = {}

        self.__response_status = None
        self.__response_body = None
        self.__response_headers = None


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

        self.__request_headers = {}

        logger.info("Request (type: '%s', method '%s') is sent to %s." % (connection_type, method, endpoint))
        logger.info("%s %s" % (method, url))
        if body is not None:
            logger.info("%s" % body)

        response = connection.getresponse()
        self.__response_status = response.status
        self.__response_headers = response.headers
        self.__response_body = response.read().decode('utf-8')

        connection.close()


    def send_http_request(self, method, url, body=None):
        self.__send_request('http', method, url, body)


    def send_https_request(self, method, url, body=None):
        self.__send_request('https', method, url, body)


    def set_request_header(self, key, value):
        self.__request_headers[key] = value


    def get_response_status(self):
        status = self.__response_status
        self.__response_status = None
        return status


    def get_response_headers(self):
        headers = self.__response_headers
        self.__response_headers = None
        return headers


    def get_response_body(self):
        body = self.__response_body
        self.__response_body = None
        return body



class Server:
    def __init__(self):
        self.__response_headers = {}
        self.__request = None

        self.__server = None
        self.__thread = None


    def start_server(self, host, port):
        logger.info("Prepare HTTP server '%s:%s' and thread to serve it." % (host, port))

        self.__server = HttpServer(host, int(port))
        self.__thread = threading.Thread(target=self.__server.start, args=())
        self.__thread.start()


    def stop_server(self):
        if self.__server is not None:
            self.__server.stop()
            self.__thread.join()


    def wait_for_request(self):
        self.__request = RequestStorage.pop()
        if self.__request is None:
            raise AssertionError("Timeout: request was not received.")

        logger.info("Request is received: %s" % self.__request)


    def get_request_method(self):
        return self.__request.get_method()


    def get_request_body(self):
        return self.__request.get_body()


    def get_request_url(self):
        return self.__request.get_url()


    def set_reply_header(self, key, value):
        self.__response_headers[key] = value


    def reply_by(self, status, body=None):
        response = Response(int(status), body, self.__response_headers)
        ResponseStorage.push(response)



class Json:
    @staticmethod
    def get_json_value(json_string, path):
        json_content = json.loads(json_string)
        keys = path.split('/')

        current_element = json_content
        for key in keys:
            current_element = current_element[key]

        return current_element


    @staticmethod
    def set_json_value(json_string, path, value):
        json_content = json.loads(json_string)
        keys = path.split('/')

        current_element = json_content
        for key in keys:
            if key == keys[-1]:
                current_element[key] = value
            else:
                current_element = current_element[key]

        return json.dumps(json_content)
