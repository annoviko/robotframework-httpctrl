"""!

@brief Synchronous queue to store responses.

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

import threading

from copy import copy
from robot.api import logger


class ResponseStorage:
    __response = None
    __response_condition = threading.Condition()

    @staticmethod
    def __ready():
        return ResponseStorage.__response is not None

    @staticmethod
    def push(response):
        with ResponseStorage.__response_condition:
            logger.info("Push response to the Response Storage: %s" % response)
            ResponseStorage.__response = response
            ResponseStorage.__response_condition.notify()

    @staticmethod
    def pop(timeout=5.0):
        with ResponseStorage.__response_condition:
            if ResponseStorage.__response is None:
                result = ResponseStorage.__response_condition.wait_for(ResponseStorage.__ready, timeout)
                if result is True:
                    logger.info("Pop response from the Response Storage: %s" % ResponseStorage.__response)
                else:
                    logger.info("Timeout - no response is obtained from Response Storage.")

            response = copy(ResponseStorage.__response)
            ResponseStorage.__response = None

        return response
