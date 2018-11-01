import os
import logging


class AppLog(object):
    def __init__(self):
        self.__log_path = os.path.abspath(os.path.join(os.path.dirname(__file__) + '/app.log'))
        self.handler = logging.FileHandler(self.__log_path)
        self.formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(process)d %(thread)d '
            '%(pathname)s %(lineno)s %(message)s'
        )
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(logging.DEBUG)


class DebugFalseLog(AppLog):
    def __init__(self):
        super(DebugFalseLog, self).__init__()
        self.handler.setLevel(logging.ERROR)

    def get_handler(self):
        return self.handler