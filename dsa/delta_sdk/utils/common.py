import time
import json
from pytz import timezone
from datetime import datetime
import sys
from delta_sdk.utils import logging
from delta_sdk.configs.common import CommonConfig
from typing import Callable
import pandas as pd

class DelayType:
    LINEAR = "linear"
    EXPONENTIAL = "exponential"

class SingletonMeta(type):
    """SingleTon Meta"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = ('|'.join(args), '|'.join([f"{key}:{value if value else ''}" for key, value in kwargs.items()]))
        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]

class RateLimiter(metaclass=SingletonMeta):
    """Ratelimiter Generator
        Args::
            name: | Optional
            mode: | Optional
            tps: | when mode is 'regular_interval'
            ceiling: | when mode is 'by_ceiling'
            time_window: | when mode is 'by_ceiling'
    """

    class RateLimiterModes:
        REGULAR_INTERVAL = 'regular_interval'
        BY_CEILING = "by_ceiling"

    mode = RateLimiterModes

    def __init__(self, name='ratelimiter', mode=mode.REGULAR_INTERVAL, tps=None, ceiling=None, time_window=None):
        self.name = name
        self.mode = mode

        if self.mode == RateLimiter.mode.BY_CEILING:

            if not (ceiling and time_window):
                ValueError("Either 'ceiling' or ''time_window' not provided.")

            self.strategy = self.next_by_ceiling
            self.freq = 0
            self.ceiling = ceiling
            self.start_time = time.time()
            self.time_window = time_window

        elif self.mode == RateLimiter.mode.REGULAR_INTERVAL:

            if not (tps): raise ValueError("'tps' not provided.")
            self.strategy = self.next_by_regular_interval
            self.time_window = (1/tps)

    def __iter__(self):
        return self

    def next_by_regular_interval(self):
        if delay:= ( time.time() - self.last_called - self.time_window ) > 0 :
            logging.info(f"wait for {delay} seconds")
            time.sleep(delay)
        self.last_called = time.time()

    def next_by_ceiling(self):
        self.freq += 1
        current_time = time.time()
        if current_time > self.start_time + self.time_window:
            self.start_time = current_time
            self.freq = 0

        if self.freq > self.ceiling:
            delay = self.start_time + self.time_window - current_time
            logging.info(f"Ceiling hit . Please wait for {delay} seconds")
            time.sleep(delay)

    def __next__(self):
        self.strategy()
        return True

class CommonUtils:

    @staticmethod
    def retry_connection(max_retries=1, delay=1,exceptions: tuple=(Exception,), delay_type: str=DelayType.LINEAR, rate_limiter: RateLimiter=None):
        """
            Args::
                max_retries | optional
                delay | Optional
                exceptions | Optional | By default Retries for any Exception.

        """
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                retries_left = max_retries
                nonlocal delay
                while retries_left >0:
                    try:
                        if rate_limiter: next(rate_limiter)
                        return func(*args, **kwargs)
                    except exceptions as e:
                        retries_left -= 1
                        logging.error(f"{type(e).__name__}:{e}")
                        if delay_type == DelayType.EXPONENTIAL and retries_left < max_retries-1: delay *= 2
                        logging.info(f"Retries left : {retries_left} | Delaying for {str(delay)} sec")
                        time.sleep(delay)

                raise RuntimeError(f"Falied after {max_retries} attempts")
            return inner_wrapper
        return wrapper

    @staticmethod
    def getCurrentTS():
        tz = timezone(CommonConfig.TIMEZONE_CONFIG)
        local_time = datetime.now(tz)
        return local_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @staticmethod
    def write_file(file_path, data):
        try:
            with open(file_path, 'w') as file:
                file.write(data)
        except IOError as e:
            logging.info(f"Failed to write to {file_path}: {e}")

    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except (IOError, json.JSONDecodeError) as e:
            logging.info(f"Failed to read from {file_path}: {e}")
            return {}

    @staticmethod
    def execution_time_calc_decorator(func):
        def wrapper(*args, **kwargs):
            fname = func.__name__
            logging.info(f"Function currently running : {fname}")
            start_time = time.time()
            output = func(*args, **kwargs)
            end_time = time.time()
            logging.info(f" {fname} Total Time Taken : {end_time - start_time}")
            return output
        return wrapper
    
class Counter:
    def __init__(self):
        self._count = 0
    def increment_count(self):
        self._count += 1
    def get_count(self):
        return self._count
    def __str__(self):
        return str(self._count)
    def __int__(self):
        return self.get_count()
    def __iadd__(self, value):
        if isinstance(value, int):
            self.increment_count()
            return self
        raise TypeError("Only integers can be added")
    
def parse_yaml_config_data(yaml_data):

    from functools import reduce
    import re
    import yaml

    yaml_content = None

    if isinstance(yaml_data, bytes):
        yaml_content = yaml.load(yaml_data, Loader=yaml.Loader)

    def _get(pdict, plist):
        return reduce(lambda d, k: d[k], plist, pdict)

    def _replace(obj):
        for k, v in obj.items():
            if isinstance(v, dict):
                _replace(v)
            if isinstance(v, str):
                match = re.match(r'.*\$\{(.*)\}.*', v)
                if match:
                    reference = match.group(1).split('.')
                    replace = _get(yaml_content, reference)
                    obj[k] = re.sub(r'\$\{(.*)\}', replace, v)

    _replace(yaml_content)
    return yaml_content
class BatchExec:

    def __init__(self, batch_size=sys.maxsize):
        self.batch_no = 0
        self.start = 0
        self.end = 0
        self.batch_size = batch_size
        self.df_batch_rows = None
        self.total_len = None
        self.terminate = False

        logging.info(f"Batch size set to :{batch_size}")

    def batch_log(self, status, message):
        batch_log = {
            "batch_number": self.batch_no,
            "batch_start": self.start,
            "batch_end": self.end - 1,
            "status": status,
            "rows": self.df_batch_rows,
            "message": message
        }
        return batch_log

    def trigger_in_df_batches(self, func: Callable, dataframe: pd.DataFrame, *args, **kwargs):

        if not self.total_len:
            self.total_len = len(dataframe)
        message = ''

        self.start = self.end
        self.end = self.start + self.batch_size

        if self.end >= self.total_len:
            self.terminate = True
            self.end = self.total_len

        try:
            df_batch = dataframe.iloc[self.start:self.end]
            self.df_batch_rows = len(df_batch)
            logging.info(f"function: {func.__name__} | start: {self.start} | end: {self.end} | batch_size: {self.df_batch_rows}")
            message = func(df_batch=df_batch, *args, **kwargs)
            status = "success"
        except Exception as e:
            message = f"{type(e).__name__}:{e}"
            status = "error"
        finally:
            batch_log = self.batch_log(status=status, message=message)
            logging.info(batch_log)

            if not self.terminate:
                self.trigger_in_df_batches(func, dataframe, *args, **kwargs)