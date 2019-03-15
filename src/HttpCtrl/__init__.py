"""!

@brief HTTP(S) client and server API that is provided to Robot Framework.

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

import http.client
import json
import threading

from robot.api import logger

from HttpCtrl.http_server import HttpServer
from HttpCtrl.request_storage import RequestStorage
from HttpCtrl.response_storage import ResponseStorage
from HttpCtrl.response import Response


class Client:
    """

    HTTP/HTTPS Client Library that provides comprehensive interface to Robot Framework.

    Example how to send GET request to obtain origin IP address and check that response is not empty:

    .. code:: robotframework

        *** Settings ***

        Library         HttpCtrl.Client
        Library         HttpCtrl.Json


        *** Test Cases ***

        Get Origin Address
            Initialize Client   www.httpbin.org
            Send HTTP Request   GET   /ip

            ${response status}=   Get Response Status
            ${response body}=     Get Response Body

            ${expected status}=   Convert To Integer   200
            Should Be Equal   ${response status}   ${expected status}

            ${origin}=    Get Json Value   ${response body}   origin
            Should Not Be Empty   ${origin}

    Example how to sent PATCH request using HTTPS:

    .. code:: robotframework

        *** Settings ***

        Library         HttpCtrl.Client
        Library         HttpCtrl.Json

        *** Test Cases ***

        Send HTTPS PATCH Request
            Initialize Client   www.httpbin.org

            ${body}=   Set Variable   { "volume": 77, "mute": false }
            Send HTTPS Request   PATCH   /patch   ${body}

            ${response status}=   Get Response Status
            ${response body}=     Get Response Body

            ${expected status}=   Convert To Integer   200
            Should Be Equal   ${response status}   ${expected status}

            ${volume}=   Get Json Value   ${response body}   json/volume
            Should Be Equal   ${volume}   ${77}

            ${mute}=   Get Json Value   ${response body}   json/mute
            Should Be Equal   ${mute}   ${False}

    """

    def __init__(self):
        self.__host = None
        self.__port = None

        self.__request_headers = {}

        self.__response_status = None
        self.__response_body = None
        self.__response_headers = None


    def initialize_client(self, host, port=None):
        """

        Initialize client using host and port of a server which will be used for communication.

        `host` [in] (string): Host of a server which client will use for communication.

        `port` [in] (string|integer): Port of a server which client will use for communication. Optional argument.

        Example when server is located on machine with address 192.168.0.1 and port 8000:

        +-------------------+-------------+------+
        | Initialize Client | 192.168.0.1 | 8000 |
        +-------------------+-------------+------+

        .. code:: robotframework

            Initialize Client   192.168.0.1   8000

        Example when your server has name:

        +-------------------+-----------------+
        | Initialize Client | www.httpbin.org |
        +-------------------+-----------------+

        .. code:: robotframework

            Initialize Client   www.httpbin.org

        """
        self.__host = host
        self.__port = port or ""


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
        """

        Send HTTP request with specified parameters.

        `method` [in] (string): Method that is used to send request (GET, POST, PUT, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        `body` [in] (string): Body of the request.

        Example where GET request is sent to server:

        +-------------------+-----+-----+
        | Send HTTP Request | GET | /ip |
        +-------------------+-----+-----+

        .. code:: robotframework

            Send HTTP Request   GET   /ip

        Example where POST request is sent with specific body:

        +-------------------+------+-------+-------------------------------+
        | Send HTTP Request | POST | /post | { "message": "Hello World!" } |
        +-------------------+------+-------+-------------------------------+

        .. code:: robotframework

            ${body}=   Set Variable   { "message": "Hello World!" }
            Send HTTP Request   POST   /post   ${body}

        """
        self.__send_request('http', method, url, body)


    def send_https_request(self, method, url, body=None):
        """

        Send HTTPS request with specified parameters.

        `method` [in] (string): Method that is used to send request (GET, POST, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        `body` [in] (string): Body of the request.

        Example where PATCH request to update parameters:

        +--------------------+-------+--------+---------------------------------+
        | Send HTTPS Request | PATCH | /patch | { "volume": 77, "mute": false } |
        +--------------------+-------+--------+---------------------------------+

        .. code:: robotframework

            ${body}=   Set Variable   { "volume": 77, "mute": false }
            Send HTTPS Request   PATCH   /patch   ${body}

        """
        self.__send_request('https', method, url, body)


    def set_request_header(self, key, value):
        """

        Set HTTP header for request that is going to be sent. Should be called before 'Send HTTP Request' or
        'Send HTTPS Request'.

        `key` [in] (string): Header name that should be used in the request (be aware of case-sensitive headers).

        `value` [in] (string): Value that corresponds to specified header.

        Example where several specific headers 'Content-Type' and 'Some Header' are set to request:

        +--------------------+------------------+-------------------+
        | Set Request Header | Important-Header | important-value   |
        +--------------------+------------------+-------------------+
        | Set Request Header | Some-Header      | some-value-for-it |
        +--------------------+------------------+-------------------+

        .. code:: robotframework

            Set Request Header   Important-Header   important-value
            Set Request Header   Some-Header        some-value-for-it

        """
        self.__request_headers[key] = value


    def get_response_status(self):
        """

        Return response code as an integer value. This method should be called once after 'Send HTTP Request' or
        'Send HTTPS Request'. It returns None, in case of attempt to get response code more then once or if
        'Send HTTP Request' or 'Send HTTPS Request' is not called before.

        Example how to get response code:

        +---------------------+---------------------+
        | ${response status}= | Get Response Status |
        +---------------------+---------------------+

        .. code:: robotframework

            ${response status}=   Get Response Status

        """
        status = self.__response_status
        self.__response_status = None
        return status


    def get_response_headers(self):
        """

        Return response headers as a dictionary. This method should be called once after 'Send HTTP Request' or
        'Send HTTPS Request'. It returns None, in case of attempt to get response code more then once or if
        'Send HTTP Request' or 'Send HTTPS Request' is not called before.

        Example how to get response code:

        +----------------------+----------------------+
        | ${response headers}= | Get Response Headers |
        +----------------------+----------------------+

        .. code:: robotframework

            ${response headers}=   Get Response Headers

        """
        headers = self.__response_headers
        self.__response_headers = None
        return headers


    def get_response_body(self):
        """

        Return response body as a string. This method should be called once after 'Send HTTP Request' or
        'Send HTTPS Request'. It returns None, in case of attempt to get response code more then once or if
        'Send HTTP Request' or 'Send HTTPS Request' is not called before.

        Example how to get response code:

        +-------------------+-------------------+
        | ${response body}= | Get Response Body |
        +-------------------+-------------------+

        .. code:: robotframework

            ${response body}=   Get Response Body

        """
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


    def get_request_headers(self):
        return self.__request.get_headers()


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
