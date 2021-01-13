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

import ipaddress
import socket
import threading

from socketserver import TCPServer

from robot.api import logger

from HttpCtrl.http_handler import HttpHandler
from HttpCtrl.internal_messages import TerminationRequest
from HttpCtrl.response_storage import ResponseStorage


class TCPServerIPv6(TCPServer):
    address_family = socket.AF_INET6


class HttpServer:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

        self.__handler = None
        self.__server = None

        self.__is_run_state = False
        self.__cv_run = threading.Condition()


    def __del__(self):
        if self.__server is not None:
            self.stop()


    def start(self):
        TCPServer.allow_reuse_address = True

        self.__handler = HttpHandler
        self.__server = self.__create_tcp_server()

        try:
            with self.__cv_run:
                self.__is_run_state = True
                self.__cv_run.notify()

            self.__server.serve_forever()

        except Exception as exception:
            self.stop()
            raise exception


    def wait_run_state(self):
        with self.__cv_run:
            while not self.__is_run_state:
                self.__cv_run.wait()


    def stop(self):
        if self.__server is not None:
            ResponseStorage().push(TerminationRequest())

            self.__server.shutdown()
            self.__server.server_close()
            self.__server = None

            with self.__cv_run:
                self.__is_run_state = False


    def __create_tcp_server(self):
        tcp_server = self.__create_ipv6_tcp_server()
        if tcp_server is not None:
            return tcp_server

        return self.__create_ipv4_tcp_server()


    def __create_ipv6_tcp_server(self):
        try:
            ipaddress.IPv6Address(self.__host)  # if throws exception then address is not IPv6

            tcp_server = TCPServerIPv6((self.__host, self.__port), self.__handler)

            logger.info("IPv6 TCP server '%s:%s' is created for HTTP." % (self.__host, str(self.__port)))

            return tcp_server
        except:
            return None


    def __create_ipv4_tcp_server(self):
        tcp_server = TCPServer((self.__host, self.__port), self.__handler)

        logger.info("IPv4 TCP server '%s:%s' is created for HTTP." % (self.__host, str(self.__port)))

        return tcp_server
