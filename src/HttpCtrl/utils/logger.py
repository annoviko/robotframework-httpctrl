"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""


from robot.api import logger


class LoggerAssistant:
    __MAX_BODY_SIZE_TO_LOG = 512


    @staticmethod
    def set_body_size(body_size):
        if body_size is None:
            logger.info("Disable the limit for the body size to log.")
        else:
            logger.info("Set the limit for the body size to log: '%d'." % body_size)

        LoggerAssistant.__MAX_BODY_SIZE_TO_LOG = body_size


    @staticmethod
    def get_body(body):
        if body is not None:
            if (LoggerAssistant.__MAX_BODY_SIZE_TO_LOG is None) or (len(body) < LoggerAssistant.__MAX_BODY_SIZE_TO_LOG):
                return body
            else:
                return "%s...\n...\n<display only the first '%d' from '%d' symbols>" % (body[:LoggerAssistant.__MAX_BODY_SIZE_TO_LOG], LoggerAssistant.__MAX_BODY_SIZE_TO_LOG, len(body))

        return ""
