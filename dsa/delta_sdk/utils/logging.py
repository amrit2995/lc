import logging
from delta_sdk.utils.common import CommonConfig

class SingletonType(type):
    """A metaclass for creating Singleton classes."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=SingletonType):
    """A Singleton Logger class to ensure a single logger instance."""

    def __init__(self):
        self.logger = logging.getLogger('delta.logger')
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter(CommonConfig.DEFAULT_LOG_FORMAT)

            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def error(self, *logline):
        logs_str = ' '.join(str(arg) for arg in logline)
        self.logger.error(logs_str)

    def info(self, *logline):
        logs_str = ' '.join(str(arg) for arg in logline)
        self.logger.info(logs_str)

    def critical(self, *logline):
        logs_str = ' '.join(str(arg) for arg in logline)
        self.logger.critical(logs_str)

    def warning(self, *logline):
        logs_str = ' '.join(str(arg) for arg in logline)
        self.logger.warning(logs_str)

def error(*logline):
    Logger().error(*logline)

def info(*logline):
    Logger().info(*logline)

def critical(*logline):
    Logger().critical(*logline)

def warning(*logline):
    Logger().warning(*logline)