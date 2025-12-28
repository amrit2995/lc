import sys

class REQUEST_CONFIG:
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_DELAY: 2

class CommonConfigs:
    TIMEZONE_CONFIG = "US/Eastern"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s %(levelname)s - %(message)s"
    DEFAULT_MATERIALISATION_DATASET_IN_MINS = 500
    DEFAULT_BATCH_SIZE = sys.maxsize
    DEFAULT_DAILY_DAYS_PERIOD = 7
    DEFAULT_DATASET_EXPIRY_IN_MINS = 60