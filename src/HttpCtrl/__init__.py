"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""

import datetime
import http.client
import json
import threading

from robot.api import logger

from HttpCtrl.utils.logger import LoggerAssistant

from HttpCtrl.internal_messages import IgnoreRequest
from HttpCtrl.http_server import HttpServer
from HttpCtrl.http_stub import HttpStubContainer, HttpStubCriteria
from HttpCtrl.request_storage import RequestStorage
from HttpCtrl.response_storage import ResponseStorage
from HttpCtrl.response import Response


class Client:
    """

    HTTP/HTTPS Client library that provides comprehensive interface to Robot Framework to control HTTP/HTTPS client.

    See other HttpCtrl libraries:

    - HttpCtrl.Server_ - HTTP Server API for testing where easy-controlled HTTP server is required.

    - HttpCtrl.Json_ - Json related API for testing where work with Json message is required.

    - HttpCtrl.Logging_ - Logging related API to configure the logging system that is used by HttpCtrl library.

    .. _HttpCtrl.Server: server.html
    .. _HttpCtrl.Json: json.html
    .. _HttpCtrl.Logging: logging.html

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

            ${origin}=    Get Json Value From String   ${response body}   origin
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
            ${response body}=     Decode Bytes To String   ${response body}   UTF-8

            ${expected status}=   Convert To Integer   200
            Should Be Equal   ${response status}   ${expected status}

            ${volume}=   Get Json Value From String   ${response body}   json/volume
            Should Be Equal   ${volume}   ${77}

            ${mute}=   Get Json Value From String   ${response body}   json/mute
            Should Be Equal   ${mute}   ${False}

    """

    def __init__(self):
        self.__server_host = None
        self.__server_port = None
        self.__client_host = None
        self.__client_port = None

        self.__request_headers = {}

        self.__response_guard = threading.Lock()
        self.__response_status = None
        self.__response_message = None
        self.__response_body_filename = None
        self.__response_body = None
        self.__response_headers = None

        self.__event_queue = threading.Condition()
        self.__async_queue = {}


    def initialize_client(self, server_host, server_port=None, client_host=None, client_port=0):
        """

        Initialize client using host and port of a server which will be used for communication.

        `server_host` [in] (string): Host of a server that is going to be used for communication by a client.

        `server_port` [in] (string|integer): Port of a server that is going to be used for communication by a client. Optional argument.

        `client_host` [in] (string): Host of a client (source) that is used to bind. Optional argument.

        `client_port` [in] (string|integer): Port of a client (source) that is used to bind. Optional argument.

        Example when server is located on a machine with address 192.168.0.1 and port 8000:

        +-------------------+-------------+------+
        | Initialize Client | 192.168.0.1 | 8000 |
        +-------------------+-------------+------+

        Example when server is located on a machine with IPv6 address 0000:0000:0000:0000:0000:0000:0000:0001 and port 8000:

        +-------------------+-----------------------------------------+------+
        | Initialize Client | 0000:0000:0000:0000:0000:0000:0000:0001 | 8000 |
        +-------------------+-----------------------------------------+------+

        .. code:: text

            Initialize Client   192.168.0.1   8000

        Example when your server has name:

        +-------------------+-----------------+
        | Initialize Client | www.httpbin.org |
        +-------------------+-----------------+

        .. code:: text

            Initialize Client   www.httpbin.org

        Example when a client is bind to the specific address 192.168.0.1 and port 8001:

        +-------------------+-------------+------+-------------+------+
        | Initialize Client | 192.168.0.5 | 8000 | 192.168.0.1 | 8001 |
        +-------------------+-------------+------+-------------+------+

        .. code:: text

            Initialize Client   192.168.0.5   8000   192.168.0.1   8001

        Example when a client is bind to the specific address only 192.168.0.1 (without port):

        +-------------------+-------------+------+-------------+
        | Initialize Client | 192.168.0.5 | 8000 | 192.168.0.1 |
        +-------------------+-------------+------+-------------+

        .. code:: text

            Initialize Client   192.168.0.5   8000   192.168.0.1

        """
        self.__server_host = server_host
        self.__server_port = server_port or ""

        self.__client_host = client_host
        self.__client_port = client_port


    def __get_source_address(self):
        if self.__client_host is None:
            return None

        return self.__client_host, int(self.__client_port)


    def __send(self, connection_type, method, url, body):
        if self.__server_host is None or self.__server_port is None:
            raise AssertionError("Client is not initialized (host and port are empty).")

        endpoint = "%s:%s" % (self.__server_host, str(self.__server_port))
        source_address = self.__get_source_address()

        logger.info("Connect to the server (type: '%s', endpoint: '%s')" % (connection_type, endpoint))

        if connection_type == 'http':
            connection = http.client.HTTPConnection(endpoint, source_address=source_address)
        elif connection_type == 'https':
            connection = http.client.HTTPSConnection(endpoint, source_address=source_address)
        else:
            raise AssertionError("Internal error of the client, please report to "
                                 "'https://github.com/annoviko/robotframework-httpctrl/issues'.")

        logger.info("Send request to the server (method: '%s', url: '%s')." % (method, url))
        try:
            connection.request(method, url, body, self.__request_headers)
        except Exception as exception:
            logger.info("Impossible to send request to the server (reason: '%s')." % str(exception))

        self.__request_headers = {}

        logger.info("Request (type: '%s', method '%s') was sent to '%s'." % (connection_type, method, endpoint))
        logger.info("%s %s" % (method, url))
        if body is not None:
            body_to_log = LoggerAssistant.get_body(body)
            logger.info("%s" % body_to_log)

        return connection


    def __read_body_to_file(self, server_response, filename):
        logger.info("Write body to file '%s'." % filename)

        default_chunk_size = 10000000   # 10 MByte
        with open(filename, "wb") as file_stream:
            while True:
                obtained_chunk = server_response.read(default_chunk_size)
                if not obtained_chunk:
                    break

                file_stream.write(obtained_chunk)


    def __wait_response(self, connection, read_body_to_file):
        try:
            server_response = connection.getresponse()

            with self.__response_guard:
                self.__response_status = server_response.status
                self.__response_message = server_response.msg
                self.__response_headers = server_response.headers

                if read_body_to_file is None:
                    self.__response_body_filename = None
                    self.__response_body = server_response.read()
                else:
                    self.__response_body_filename = read_body_to_file
                    self.__response_body = None
                    
                    self.__read_body_to_file(server_response, read_body_to_file)


        except Exception as exception:
            logger.info("Server has not provided response to the request (reason: %s)." % str(exception))

        finally:
            connection.close()


    def __wait_response_async(self, connection, read_body_to_file):
        try:
            server_response = connection.getresponse()

            with self.__event_queue:
                if read_body_to_file is None:
                    response_body_file = None
                    response_body = server_response.read()

                else:
                    response_body_file = read_body_to_file
                    response_body = None

                    self.__read_body_to_file(server_response, read_body_to_file)

                headers = server_response.getheaders()
                headers_dict = {}
                if headers is not None:
                    for key, value in headers:
                        headers_dict[key] = value

                response_instance = Response(server_response.status, server_response.reason,
                                             response_body, response_body_file,
                                             headers_dict)

                self.__async_queue[connection] = response_instance
                self.__event_queue.notify_all()

        except Exception as exception:
            logger.info("Server has not provided response to the request (reason: %s)." % str(exception))

        finally:
            connection.close()


    def __send_request(self, connection_type, method, url, body, read_body_to_file):
        connection = self.__send(connection_type, method, url, body)
        self.__wait_response(connection, read_body_to_file)


    def __sent_request_async(self, connection_type, method, url, body, read_body_to_file):
        connection = self.__send(connection_type, method, url, body)

        wait_thread = threading.Thread(target=self.__wait_response_async, args=(connection, read_body_to_file))
        wait_thread.daemon = True
        wait_thread.start()

        return connection


    def send_http_request(self, method, url, body=None, resp_body_to_file=None):
        """

        Send HTTP request with specified parameters. This function is blocked until server replies or
        timeout connection.

        `method` [in] (string): Method that is used to send request (GET, POST, PUT, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        `body` [in] (string): Body of the request.

        `resp_body_to_file` [in] (string): Path to file where response body should be written. By default is `None` - response 
        body is writing in RAM. It is useful to write response body into a file when it is expected to be big enough to keep
        it in the memory.

        Example where GET request is sent to server:

        +-------------------+-----+-----+
        | Send HTTP Request | GET | /ip |
        +-------------------+-----+-----+

        .. code:: text

            Send HTTP Request   GET   /ip

        Example where POST request is sent with specific body:

        +-------------------+------+-------+-------------------------------+
        | Send HTTP Request | POST | /post | { "message": "Hello World!" } |
        +-------------------+------+-------+-------------------------------+

        .. code:: text

            ${body}=   Set Variable   { "message": "Hello World!" }
            Send HTTP Request   POST   /post   ${body}
        
        Example where GET request is sent and where response body is written into a file:

        +-------------------+-----+--------------------+-----------------------------------+
        | Send HTTP Request | GET | /download_big_file | resp_body_to_file=big_archive.tar |
        +-------------------+-----+--------------------+-----------------------------------+

        .. code:: text

            Send HTTP Request   GET   /download_big_file   resp_body_to_file=big_archive.tar

        """
        self.__send_request('http', method, url, body, resp_body_to_file)


    def send_http_request_async(self, method, url, body=None, resp_body_to_file=None):
        """

        Send HTTP request with specified parameters asynchronously. Non-blocking function to send request that waits
        for reply using separate thread. Return connection object that is used as a key to get asynchronous response
        using function 'Get Async Response'.

        `method` [in] (string): Method that is used to send request (GET, POST, PUT, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        `body` [in] (string): Body of the request.

        `resp_body_to_file` [in] (string): Path to file where response body should be written. By default is `None` - response 
        body is writing in RAM. It is useful to write response body into a file when it is expected to be big enough to keep
        it in the memory.

        Example where PUT request is sent with specific body:

        +----------------+-------------------------+-----+------+---------------+
        | ${connection}= | Send HTTP Request Async | PUT | /put | Hello Server! |
        +----------------+-------------------------+-----+------+---------------+

        .. code:: text

            ${connection}=   Send HTTP Request Async   PUT   /put   Hello Server!

        Example where GET request is sent and where response body is written into a file:

        +----------------+-------------------------+-----+--------------------+-----------------------------------+
        | ${connection}= | Send HTTP Request Async | GET | /download_big_file | resp_body_to_file=big_archive.tar |
        +----------------+-------------------------+-----+--------------------+-----------------------------------+

        .. code:: text

            ${connection}=   Send HTTP Request Async   GET   /download_big_file   resp_body_to_file=big_archive.tar

        """
        return self.__sent_request_async('http', method, url, body, resp_body_to_file)


    def send_https_request(self, method, url, body=None, resp_body_to_file=None):
        """

        Send HTTPS request with specified parameters.

        `method` [in] (string): Method that is used to send request (GET, POST, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        `body` [in] (string): Body of the request.

        `resp_body_to_file` [in] (string): Path to file where response body should be written. By default is `None` - response 
        body is writing in RAM. It is useful to write response body into a file when it is expected to be big enough to keep
        it in the memory.

        Example where PATCH request to update parameters:

        +--------------------+-------+--------+---------------------------------+
        | Send HTTPS Request | PATCH | /patch | { "volume": 77, "mute": false } |
        +--------------------+-------+--------+---------------------------------+

        .. code:: text

            ${body}=   Set Variable   { "volume": 77, "mute": false }
            Send HTTPS Request   PATCH   /patch   ${body}

        """
        self.__send_request('https', method, url, body, resp_body_to_file)


    def send_https_request_async(self, method, url, body=None, resp_body_to_file=None):
        """

        Send HTTPS request with specified parameters asynchronously. Non-blocking function to send request that waits
        for reply using separate thread. Return connection object that is used as a key to get asynchronous response
        using function 'Get Async Response'.

        `method` [in] (string): Method that is used to send request (GET, POST, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        `body` [in] (string): Body of the request.

        `resp_body_to_file` [in] (string): Path to file where response body should be written. By default is `None` - response 
        body is writing in RAM. It is useful to write response body into a file when it is expected to be big enough to keep
        it in the memory.

        Example where DELETE request is sent with specific body:

        +----------------+--------------------------+--------+---------+
        | ${connection}= | Send HTTPS Request Async | DELETE | /delete |
        +----------------+--------------------------+--------+---------+

        .. code:: text

            ${connection}=   Send HTTPS Request Async   DELETE   /delete

        """
        return self.__sent_request_async('https', method, url, body, resp_body_to_file)


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

        .. code:: text

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

        .. code:: text

            ${response status}=   Get Response Status

        """
        with self.__response_guard:
            status = self.__response_status
            self.__response_status = None
            return status


    def get_response_message(self):
        with self.__response_guard:
            message = self.__response_message
            self.__response_message = None
            return message


    def get_response_headers(self):
        """

        Return response headers as a dictionary. This method should be called once after 'Send HTTP Request' or
        'Send HTTPS Request'. It returns None, in case of attempt to get response code more then once or if
        'Send HTTP Request' or 'Send HTTPS Request' is not called before.

        Example how to get response code:

        +----------------------+----------------------+
        | ${response headers}= | Get Response Headers |
        +----------------------+----------------------+

        .. code:: text

            ${response headers}=   Get Response Headers

        """
        with self.__response_guard:
            headers = self.__response_headers
            self.__response_headers = None
            return headers


    def get_response_body(self):
        """

        Return response body as a byte array. This method should be called once after 'Send HTTP Request' or
        'Send HTTPS Request'. It returns None, in case of attempt to get response code more then once or if
        'Send HTTP Request' or 'Send HTTPS Request' is not called before.

        Example how to get response code:

        +-------------------+-------------------+
        | ${response body}= | Get Response Body |
        +-------------------+-------------------+

        .. code:: text

            ${response body}=   Get Response Body

        """
        with self.__response_guard:
            body = None

            if self.__response_body is not None:
                body = self.__response_body

            elif self.__response_body_filename is not None:
                with open(self.__response_body_filename) as file_stream:
                    body = file_stream.read()

            self.__response_body_filename = None
            self.__response_body = None

            return body


    def get_async_response(self, connection, timeout=0):
        """

        Return response as an object for the specified connection. This method should be called once after
        'Send HTTP Request Async' or 'Send HTTPS Request Async'. It returns None if there is no response for the
        specified connection.

        `connection` [in] (object): Connection for that response should be obtained.

        `timeout` [in] (int): Period of time in seconds to obtain response (by default is 0).

        Example how to get response object:

        +--------------+--------------------+
        | ${response}= | Get Async Response |
        +--------------+--------------------+

        Example how to try to get response object during 10 seconds:

        +--------------+--------------------+----+
        | ${response}= | Get Async Response | 10 |
        +--------------+--------------------+----+

        .. code:: text

            ${connection}=   Send HTTP Async Request   POST            /post   Hello Server!
            ${response}=     Get Async Response        ${connection}   5

        """
        with self.__event_queue:
            start_time = datetime.datetime.now()
            end_time = start_time

            while (end_time - start_time).total_seconds() < int(timeout):
                if connection in self.__async_queue:
                    return self.__async_queue.pop(connection)

                def predicate():
                    return connection in self.__async_queue

                self.__event_queue.wait_for(predicate, int(timeout))
                end_time = datetime.datetime.now()

            return self.__async_queue.pop(connection, None)


    def get_status_from_response(self, response : Response):
        """

        Return response status as an integer value from the specified response object that was obtained by function
        'Get Async Response'. Return 'None' if response object is None.

        Example how to get response status from a response object:

        +---------------------+--------------------------+-------------+
        | ${response status}= | Get Status From Response | ${response} |
        +---------------------+--------------------------+-------------+

        .. code:: text

            ${connection}=      Send HTTP Async Request   GET             /get

            # Some other actions ...

            ${response}=          Get Async Response         ${connection}   5
            ${response status}=   Get Status From Response   ${response}

        """
        if response is None:
            logger.error("Impossible to get status from 'None' response object.")
            return None

        return response.get_status()


    def get_reason_from_response(self, response : Response):
        """

        Return response reason as a string from the specified response object that was obtained by function
        'Get Async Response'. For example, response code and reason are '200 OK', in this case 'OK' is going
        to be returned by this function.

        Example how to get response reason from a response object:

        +---------------------+--------------------------+-------------+
        | ${response reason}= | Get Reason From Response | ${response} |
        +---------------------+--------------------------+-------------+

        .. code:: text

            ${connection}=      Send HTTP Async Request   GET             /get

            # Some other actions ...

            ${response}=          Get Async Response         ${connection}   5
            ${response reason}=   Get Reason From Response   ${response}

        """
        if response is None:
            logger.error("Impossible to get reason from 'None' response object.")
            return None

        return response.get_reason()


    def get_headers_from_response(self, response : Response) -> dict:
        """

        Return response headers as a dictionary from the specified response object that was obtained by function
        'Get Async Response'. Return 'None' if response object is None.

        Example how to get response headers from a response object:

        +----------------------+---------------------------+-------------+
        | ${response headers}= | Get Headers From Response | ${response} |
        +----------------------+---------------------------+-------------+

        .. code:: text

            ${connection}=      Send HTTP Async Request   GET             /get

            # Some other actions ...

            ${response}=           Get Async Response          ${connection}   5
            ${response headers}=   Get Headers From Response   ${response}

        """
        if response is None:
            logger.error("Impossible to get headers from 'None' response object.")
            return None

        return response.get_headers()


    def get_body_from_response(self, response : Response):
        """

        Return response body as a byte array from the specified response object that was obtained by function
        'Get Async Response'. Return 'None' if response object is None.

        Example how to get response code from a response object:

        +-------------------+------------------------+-------------+
        | ${response body}= | Get Body From Response | ${response} |
        +-------------------+------------------------+-------------+

        .. code:: text

            ${connection}=      Send HTTP Async Request   GET             /get

            # Some other actions ...

            ${response}=        Get Async Response        ${connection}   5
            ${response body}=   Get Body From Response    ${response}

        """
        if response is None:
            logger.error("Impossible to get body from 'None' response object.")
            return None

        return response.get_body()



class Server:
    """

    HTTP Server library that provides comprehensive interface to Robot Framework to control HTTP server.

    See other HttpCtrl libraries:

    - HttpCtrl.Client_ - HTTP/HTTP Client API for testing where easy-controlled HTTP/HTTPS client is required.

    - HttpCtrl.Json_ - Json related API for testing where work with Json message is required.

    - HttpCtrl.Logging_ - Logging related API to configure the logging system that is used by HttpCtrl library.

    .. _HttpCtrl.Client: client.html
    .. _HttpCtrl.Json: json.html
    .. _HttpCtrl.Logging: logging.html

    Here is an example of receiving POST request. In this example HTTP client sends POST request to HTTP server. HTTP
    server receives it and checks incoming request for correctness.

    .. code:: robotframework

        *** Settings ***

        Library         String
        Library         HttpCtrl.Client
        Library         HttpCtrl.Server

        Test Setup       Initialize HTTP Client And Server
        Test Teardown    Terminate HTTP Server

        *** Test Cases ***

        Receive And Reply To POST
            ${request body}=   Set Variable   { "method": "POST" }
            Send HTTP Request Async   POST   /post   ${request body}

            Wait For Request
            Reply By   200

            ${method}=   Get Request Method
            ${url}=      Get Request Url
            ${body}=     Get Request Body
            ${body}=     Decode Bytes To String   ${body}   UTF-8

            Should Be Equal   ${method}   POST
            Should Be Equal   ${url}      /post
            Should Be Equal   ${body}     ${request body}

        *** Keywords ***

        Initialize HTTP Client And Server
            Initialize Client   127.0.0.1   8000
            Start Server        127.0.0.1   8000

        Terminate HTTP Server
            Stop Server

    In case of requirement to use IPv6 the keyword `Initialize HTTP Client And Server` might be the following:

    .. code:: robotframework

        *** Keywords ***

        Initialize HTTP Client And Server
            Initialize Client   0000:0000:0000:0000:0000:0000:0000:0001   8000
            Start Server        0000:0000:0000:0000:0000:0000:0000:0001   8000

    There is an example where server stubs are using. Sever stub is a pre-defined function that is used by the server to
    reply automatically to a request that satisfies a user specific HTTP criteria.

    .. code:: robotframework

        *** Settings ***

        Library         String
        Library         HttpCtrl.Client
        Library         HttpCtrl.Server

        Test Setup       Initialize HTTP Client And Server
        Test Teardown    Terminate HTTP Server

        *** Test Cases ***

        Set Signle Stub And Send Request
            # Set server stub to reply automatically to POST /api/v1/post
            Set Stub Reply   POST   /api/v1/post   200   Post Message

            # Send HTTP request to the server
            Send HTTP Request   POST   /api/v1/post

            # Check that the client receives pre-defined values by the stub
            ${status}=     Get Response Status
            ${body}=       Get Response Body
            ${body}=       Decode Bytes To String   ${body}   UTF-8

            Should Be Equal   ${status}   ${200}
            Should Be Equal   ${body}     Post Message

            # Check that the server receives a single request
            ${count}=      Get Stub Count   POST   /api/v1/post
            Should Be Equal   ${count}   ${1}

        *** Keywords ***

        Initialize HTTP Client And Server
            Initialize Client   127.0.0.1   8000
            Start Server        127.0.0.1   8000

        Terminate HTTP Server
            Stop Server

    """

    def __init__(self):
        self.__response_headers = {}
        self.__request = None

        self.__server = None
        self.__thread = None


    def __del__(self):
        self.stop_server()


    def start_server(self, host, port):
        """

        Start HTTP server on specific address and port. Server should be closed when it is not required, for example,
        when test is over. In case of double call of \`Start Server\`, the previous will be stopped and only then the
        next one HTTP server will be started.

        `host` [in] (string): Address that will be used by HTTP server to listen.

        `port` [in] (string): Port that will be used by HTTP server to listen.

        Example how to initialize server:

        +--------------+-----------+------+
        | Start Server | 127.0.0.1 | 8000 |
        +--------------+-----------+------+

        .. code:: text

            Start Server   127.0.0.1   8000

        It is a good practice to start server and stop it using 'Test Setup' and 'Test Teardown', for example:

        .. code:: robotframework

            *** Settings ***

            Library         HttpCtrl.Server

            Test Setup       Initialize HTTP Server
            Test Teardown    Terminate HTTP Server

            *** Test Cases ***

            HTTP Server Based Test
                Wait For Request
                Reply By   200

                # Check incoming request

            *** Keywords ***

            Initialize HTTP Server
                Start Server        127.0.0.1   8000

            Terminate HTTP Server
                Stop Server

        """

        self.stop_server()

        logger.info("Prepare HTTP server '%s:%s' and thread to serve it." % (host, port))

        self.__server = HttpServer(host, int(port))
        self.__thread = threading.Thread(target=self.__server.start, args=())
        self.__thread.start()

        # In case of start-stop, stop may be finished before server start and ir will be impossible to join thread.       
        self.__server.wait_run_state()


    def stop_server(self):
        """

        Stop HTTP server if it has been started. This function should be called if server has been started.

        Example how to stop server:

        +-------------+
        | Stop Server |
        +-------------+

        .. code:: text

            Stop Server

        It is a good practice to start server and stop it using `Test Setup` and `Test Teardown` - see example for
        \`Start Server\`.

        """
        if self.__server is not None:
            self.__server.stop()
            self.__thread.join()

            self.__response_headers = {}
            self.__request = None

            ResponseStorage().clear()
            RequestStorage().clear()
            HttpStubContainer().clear()

            self.__server = None
            self.__thread = None

            logger.info("HTTP server is stopped.")


    def wait_for_request(self, timeout=5):
        """

        Command to server to wait incoming request. This call is blocked until HTTP request arrives. Basically server
        receives all requests after \`Start Server\` and places them to internal queue. When test call function
        \`Wait For Request\` it checks the queue and if it is not empty returns the first request in the queue. If the
        queue is empty then function waits when the server receives request and place it to the queue. There is
        default time period '5 seconds' to wait request and this waiting time can be changed. If during wait time the
        request is not received then timeout error occurs.

        `timeout` [in] (int): Period of time in seconds when a request should be received by HTTP server.

        Example how to wait request.

        +------------------+
        | Wait For Request |
        +------------------+

        .. code:: text

            Wait For Request

        Example how to wait request during 2 seconds.

        +------------------+---+
        | Wait For Request | 2 |
        +------------------+---+

        .. code:: text

            Wait For Request   2

        """
        self.__request = RequestStorage().pop(int(timeout))
        if self.__request is None:
            raise AssertionError("Timeout: request was not received.")

        logger.info("Request is received: %s" % self.__request)


    def wait_for_no_request(self, timeout=5.0):
        """

        Command to server to wait for no incoming request during specific time. This call is blocked until HTTP request
        arrives or timeout. Basically server receives all requests after \`Start Server\` and places them to internal
        queue. When test call function \`Wait For No Request\` it checks the queue and if it is not empty returns throws
        exception. Otherwise it waits for request during 'timeout' seconds. If during this time request is received then
        exception is thrown.

        `timeout` [in] (int): Period of time in seconds when requests should not be received by HTTP server.

        Example how to wait for lack of requests.

        +---------------------+
        | Wait For No Request |
        +---------------------+

        .. code:: text

            Wait For No Request

        Example how to wait for lack of requests during 10 seconds.

        +---------------------+----+
        | Wait For No Request | 10 |
        +---------------------+----+

        .. code:: text

            Wait For No Request   10

        """
        self.__request = RequestStorage().pop(int(timeout))
        if self.__request is not None:
            raise AssertionError("Request was received: %s." % self.__request)

        logger.info("Request is not received.")


    def wait_and_ignore_request(self):
        """

        Command to server to wait incoming request and ignore it by closing connection. This call is blocked until HTTP
        request arrives. Basically server receives all requests after \`Start Server\` and places them to internal
        queue. When test call function \`Wait And Ignore Request\` it checks the queue and if it is not empty returns
        the first request in the queue is ignore and connection is closed. If the queue is empty then function waits
        when the server receives request and place it to the queue.

        Example how to wait and ignore request.

        +-------------------------+
        | Wait And Ignore Request |
        +-------------------------+

        .. code:: text

            Wait And Ignore Request

        """
        self.wait_for_request()
        ResponseStorage().push(IgnoreRequest())
        logger.info("Request is ignored by closing connection.")


    def set_stub_reply(self, method, url, status, body=None):
        """
        
        Sets stub reply for HTTP(S) server. This function sets a server stub to reply automatically by a specific 
        response to a specific request. When the stub is used to reply, then corresponding statistic is incremented
        (see \`Get Stub Count\`).

        `method` [in] (string): Request method that is used to handle by server stub (GET, POST, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource that is used by server stub, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        `status` [in] (int|string): HTTP status code for response that is used by server stub.

        `body` [in] (string|bytes): Response body that is used by server stub.

        Example how to set stub to reply automatically to request `POST` `/api/v1/request` by status `200`.

        +----------------+------+-----------------+-----+
        | Set Stub Reply | POST | /api/v1/request | 200 |
        +----------------+------+-----------------+-----+

        .. code:: text
        
            Set Stub Reply   POST   /api/v1/request   200
        
        Example how to set stub to reply automatically using a specific body.

        +----------------+------+-----------------+-----+--------------------------+
        | Set Stub Reply | POST | /api/v1/request | 202 | Request has been handled |
        +----------------+------+-----------------+-----+--------------------------+

        .. code:: text

            Set Stub Reply   POST   /api/v1/request   200   Request has been handled

        """
        if self.__server is None:
            message_error = "Impossible to set server stub reply (reason: 'server is not created')."
            raise AssertionError(message_error)
        
        criteria = HttpStubCriteria(method=method, url=url)
        response = Response(int(status), None, body, None, None)
        HttpStubContainer().add(criteria, response)


    def get_stub_count(self, method, url):
        """
        
        Returns server stub statistic that defines how many time the stub was used by server to reply.
        
        `method` [in] (string): Request method that is used to handle by server stub (GET, POST, DELETE, etc., see: RFC 7231, RFC 5789).

        `url` [in] (string): Path to the resource that is used by server stub, for example, in case address www.httpbin.org/ip - '/ip' is an path.

        Example how to get server stub statistic for request with `POST` method and URL `/api/v2/request`.

        +----------------+------+-----------------+
        | Get Stub Count | POST | /api/v2/request |
        +----------------+------+-----------------+

        .. code:: text

            Get Stub Count   POST   /api/v2/request

        Example how to get server stub statistic for request with `GET` method and URL `/get`

        +----------------+------+-----+
        | Get Stub Count | GET | /get |
        +----------------+------+-----+

        .. code:: text

            Get Stub Count   GET   /get

        """
        if self.__server is None:
            message_error = "Impossible to get server stub statistic (reason: 'server is not created')."
            raise AssertionError(message_error)

        criteria = HttpStubCriteria(method=method, url=url)
        return HttpStubContainer().count(criteria)


    def get_request_source_address(self):
        """

        Returns source address (client address) of received request as string value. This function should be called
        after \`Wait For Request\`, otherwise None is returned.

        Example how to obtain source address of incoming request:

        +----------------------------+
        | Get Request Source Address |
        +----------------------------+

        .. code:: text

            ${source address}=   Get Request Source Address

        """
        return self.__request.get_source_address()


    def get_request_source_port(self):
        """

        Returns source port (client port) of received request as string value. This function should be called
        after \`Wait For Request\`, otherwise None is returned.

        Example how to obtain source port of incoming request:

        +-------------------------+
        | Get Request Source Port |
        +-------------------------+

        .. code:: text

            ${source port}=   Get Request Source Port

        """
        return str(self.__request.get_source_port())


    def get_request_source_port_as_integer(self):
        """

        Returns source port (client port) of received request as integer value. This function should be called
        after \`Wait For Request\`, otherwise None is returned.

        Example how to obtain source port of incoming request:

        +------------------------------------+
        | Get Request Source Port As Integer |
        +------------------------------------+

        .. code:: text

            ${source port}=   Get Request Source Port As Integer

        """
        return self.__request.get_source_port()


    def get_request_method(self):
        """

        Returns method of received request as a string. This function should be called after \`Wait For Request\`,
        otherwise None is returned.

        Example how to obtain method of incoming request:

        +--------------------+
        | Get Request Method |
        +--------------------+

        .. code:: text

            Get Request Method

        """
        return self.__request.get_method()


    def get_request_body(self):
        """

        Returns body of received request as a string. This function should be called after \`Wait For Request\`,
        otherwise None is returned.

        Example how to obtain body of incoming request:

        +------------------+
        | Get Request Body |
        +------------------+

        .. code:: text

            Get Request Body

        """
        return self.__request.get_body()


    def get_request_headers(self):
        """

        Returns headers of received request as a dictionary. This function should be called after \`Wait For Request\`,
        otherwise None is returned.

        Example how to obtain headers of incoming request:

        +---------------------+
        | Get Request Headers |
        +---------------------+

        .. code:: text

            Get Request Headers

        """
        return self.__request.get_headers()


    def get_request_url(self):
        """

        Returns URL of received request as a string. This function should be called after \`Wait For Request\`,
        otherwise None is returned.

        Example how to obtain URL of incoming request:

        +-----------------+
        | Get Request Url |
        +-----------------+

        .. code:: text

            Get Request Url

        """
        return self.__request.get_url()


    def set_reply_header(self, key, value):
        """

        Set or insert new (if it does not exist yet) header to HTTP response. To send response itself function
        \`Reply By\` is used.

        `key` [in] (string): HTTP header name.

        `value` [in] (string): HTTP header value.

        Example how to set header for HTTP response:

        +------------------+--------+----------------+
        | Set Reply Header | Origin | 127.0.0.1:8000 |
        +------------------+--------+----------------+

        .. code:: text

            Set Reply Header   Origin   127.0.0.1:8000

        Example how to set several headers for HTTP response:

        +------------------+-------------+----------------+
        | Set Reply Header | Origin      | 127.0.0.1:8001 |
        +------------------+-------------+----------------+
        | Set Reply Header | City-Source | St.-Petersburg |
        +------------------+-------------+----------------+

        .. code:: text

            Set Reply Header   Origin        127.0.0.1:8000
            Set Reply Header   City-Source   St.-Petersburg

        """
        self.__response_headers[key] = value


    def reply_by(self, status, body=None):
        """

        Send response using specified HTTP code and body. This function should be called after \`Wait For Request\`.

        `status` [in] (string): HTTP status code for response.

        `body` [in] (string|bytes): Body that should contain response.

        Example how to reply by 204 (No Content) to incoming request:

        +----------+-----+
        | Reply By | 204 |
        +----------+-----+

        .. code:: text

            Reply By   204

        Example how to reply 200 (OK) with body to incoming request:

        +----------+-----+--------------------------+
        | Reply By | 200 | { "status": "accepted" } |
        +----------+-----+--------------------------+

        .. code:: text

            ${response body}=   Set Variable   { "status": "accepted" }
            Reply By   204   ${response body}

        Example how to reply with a body represented by a sequence of bytes:

        ..code:: text

            Wait For Request

            ${body bytes}=   Evaluate   bytes((0x0a, 0x12, 0x0a))
            Reply By   200   ${body bytes}

        """
        response = Response(int(status), None, body, None, self.__response_headers)
        ResponseStorage().push(response)


class Json:
    """

    Json library provide comprehensive interface to Robot Framework to work with JSON structures that are actively
    used for Internet communication nowadays.

    See other HttpCtrl libraries:

    - HttpCtrl.Client_ - HTTP/HTTP Client API for testing where easy-controlled HTTP/HTTPS client is required.

    - HttpCtrl.Server_ - HTTP Server API for testing where easy-controlled HTTP server is required.

    - HttpCtrl.Logging_ - Logging related API to configure the logging system that is used by HttpCtrl library.

    .. _HttpCtrl.Client: client.html
    .. _HttpCtrl.Server: server.html
    .. _HttpCtrl.Logging: logging.html

    Example where Json values are updated in a string and then read from it:

    .. code:: robotframework

        *** Settings ***

        Library         HttpCtrl.Client
        Library         HttpCtrl.Json

        *** Test Cases ***

        Write And Read Json Nesting Value
            ${json template}=   Catenate
            ...   {
            ...      "book": {
            ...         "title": "St Petersburg: A Cultural History",
            ...         "author": "Solomon Volkov",
            ...         "price": 0,
            ...         "currency": ""
            ...      }
            ...   }

            ${catalog}=   Set Json Value In String   ${json template}   book/price      ${500}
            ${catalog}=   Set Json Value In String   ${catalog}         book/currency   RUB

            ${title}=      Get Json Value From String   ${catalog}   book/title
            ${price}=      Get Json Value From String   ${catalog}   book/price
            ${currency}=   Get Json Value From String   ${catalog}   book/currency


    Here is an another example where Json array's values are updated and then read from it:

    .. code:: robotframework

        *** Settings ***

        Library         HttpCtrl.Client
        Library         HttpCtrl.Json

        *** Test Cases ***

        Write And Read Json Array Value
            ${json template}=   Catenate
            ...   {
            ...      "array": [
            ...         "red", "green", "blue", "yellow"
            ...      ]
            ...   }

            ${colors}=   Set Json Value In String   ${json template}   array/3   white

            ${red}=     Get Json Value From String   ${colors}   array/0
            ${green}=   Get Json Value From String   ${colors}   array/1
            ${blue}=    Get Json Value From String   ${colors}   array/2
            ${white}=   Get Json Value From String   ${colors}   array/3

    """

    @staticmethod
    def get_json_value_from_string(json_string, path):
        """

        Return value from Json that is represented by string. Be aware, returned value's type corresponds to its
        type in Json.

        `json_string` [in] (string): Json that is represented by string.

        `path` [in] (string): Path to Json node value.

        Example how to obtain Json value:

        +-----------+----------------------------+------------------------------------+------------+
        | ${value}= | Get Json Value From String | { "book": { "title": "Unknown" } } | book/title |
        +-----------+----------------------------+------------------------------------+------------+

        .. code:: text

            ${json}=    Catenate
            ...   {
            ...      "book": {
            ...         "title": "Unknown"
            ...      }
            ...   }
            ${value}=   Get Json Value From String   ${json}   book/title

        """
        json_content = json.loads(json_string)
        keys = path.split('/')

        current_element = json_content
        for key in keys:
            if isinstance(current_element, list):
                key = int(key)

            current_element = current_element[key]

        return current_element


    @staticmethod
    def set_json_value_in_string(json_string, path, value):
        """

        Set value in Json that is represented by string. Be aware type of updated value should correspond to its
        type in Json, otherwise type will be changed with new value.

        `json_string` [in] (string): Json that is represented by string.

        `path` [in] (string): Path to Json node value.

        `value` [in] (any): New value for the Json node.

        Example how to set Json value:

        +-----------+--------------------------+------------------------------------+------------+--------+
        | ${value}= | Set Json Value In String | { "book": { "title": "Unknown" } } | book/title | "Math" |
        +-----------+--------------------------+------------------------------------+------------+--------+

        .. code:: text

            ${json}=    Catenate
            ...   {
            ...      "book": {
            ...         "title": "Unknown"
            ...      }
            ...   }
            ${value}=   Set Json Value In String   ${json}   book/title   "Math"

        Example how to set value in Json array node:

        +-----------+--------------------------+--------------------------------------+---------+---------+
        | ${value}= | Set Json Value In String | { "array": [ "one", "two", "ten" ] } | array/2 | "three" |
        +-----------+--------------------------+--------------------------------------+---------+---------+

        .. code:: text

            ${json}=    Catenate
            ...   {
            ...      "array": [
            ...         "one", "two", "ten"
            ...      ]
            ...   }
            ${value}=   Set Json Value In String   ${json}   array/2   "three"

        """
        json_content = json.loads(json_string)
        keys = path.split('/')

        current_element = json_content
        for key in keys:
            if key == keys[-1]:
                if isinstance(current_element, list):
                    key = int(key)

                current_element[key] = value
            else:
                if isinstance(current_element, list):
                    key = int(key)

                current_element = current_element[key]

        return json.dumps(json_content)



class Logging:
    """

    Logging library provide functionality to configure the logging system that is used by HttpCtrl library.

    See other HttpCtrl libraries:

    - HttpCtrl.Client_ - HTTP/HTTP Client API for testing where easy-controlled HTTP/HTTPS client is required.

    - HttpCtrl.Server_ - HTTP Server API for testing where easy-controlled HTTP server is required.

    - HttpCtrl.Json_ - Json related API for testing where work with Json message is required.

    .. _HttpCtrl.Client: client.html
    .. _HttpCtrl.Server: server.html
    .. _HttpCtrl.Json: json.html

    """

    @staticmethod
    def set_body_size_limit_to_log(body_size):
        """

        Set body (HTTP request/response) size that is allowed to log. By default the library logs `512` symbols of the body. If the
        limit should be removed then `${None}` value can be provided to the function.

        The logging body limit protects test logs to be too large if tests use big data for testing.

        Example how to set the logging body limit to 1024 symbols:

        +----------------------------+------+
        | Set Body Size Limit To Log | 1024 |
        +----------------------------+------+

        .. code:: text

            Set Body Size Limit To Log    1024

        Example how to remove the logging body limit:

        +----------------------------+---------+
        | Set Body Size Limit To Log | ${None} |
        +----------------------------+---------+

        .. code:: text

            Set Body Size Limit To Log    ${None}

        """

        LoggerAssistant.set_body_size(body_size)
