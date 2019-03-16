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

import threading

from copy import copy
from robot.api import logger


class RequestStorage:
    __request = None
    __request_condition = threading.Condition()

    @staticmethod
    def __ready():
        return RequestStorage.__request is not None

    @staticmethod
    def push(request):
        with RequestStorage.__request_condition:
            logger.info("Push request to the Request Storage: %s" % request)
            RequestStorage.__request = request
            RequestStorage.__request_condition.notify()

    @staticmethod
    def pop(timeout=5.0):
        with RequestStorage.__request_condition:
            if RequestStorage.__request is None:
                result = RequestStorage.__request_condition.wait_for(RequestStorage.__ready, timeout)
                if result is True:
                    logger.info("Pop request from the Request Storage: %s" % RequestStorage.__request)
                else:
                    logger.info("Timeout - no request is obtained from Request Storage.")

            request = copy(RequestStorage.__request)
            RequestStorage.__request = None

        return request
