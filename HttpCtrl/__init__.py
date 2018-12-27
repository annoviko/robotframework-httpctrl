import http.client
import json


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


    def __send_request(self, connection, method, url, body):
        connection.request(method, url, body, self.__request_headers)

        response = connection.getresponse()
        self.__response_status = response.status
        self.__response_body = response.read().decode('utf-8')

        connection.close()


    def send_http_request(self, method, url, body=None):
        endpoint = "%s:%s" % (self.__host, str(self.__port))
        connection = http.client.HTTPConnection(endpoint)

        self.__send_request(connection, method, url, body)


    def send_https_request(self, method, url, body=None):
        endpoint = "%s:%s" % (self.__host, str(self.__port))
        connection = http.client.HTTPSConnection(endpoint)

        self.__send_request(connection, method, url, body)


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