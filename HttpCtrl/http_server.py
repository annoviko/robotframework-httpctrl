from socketserver import TCPServer

from HttpCtrl.http_handler import HttpHandler
from HttpCtrl.logger import Logger


class HttpServer:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

        self.__handler = None
        self.__server = None


    def __del__(self):
        if self.__server is not None:
            self.stop()


    def start(self):
        self.__handler = HttpHandler
        self.__server = TCPServer((self.__host, self.__port), self.__handler)

        try:
            self.__server.serve_forever()

        except Exception as exception:
            self.stop()
            raise exception


    def stop(self):
        if self.__server is not None:
            self.__server.shutdown()
            self.__server.server_close()

            Logger.info("HTTP server is successfully stopped.")
