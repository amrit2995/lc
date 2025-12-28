import logging
import time
from typing import Callable
import pandas as pd
import sys
import argparse
from martech_sdk.utils.rate_limiter import RateLimiter


class DelayType:
    LINEAR = "linear"
    EXPONENTIAL = "exponential"

class CommonUtils:
    @staticmethod
    def parse_arguments(arguments: list[tuple]):
        """Parse command line arguments required for the job.

        :param arguments: command line arguments. [('arg_name', is_required - boolean flag)]
        :return: list of commands line arguments
        """
        parser = argparse.ArgumentParser()
        for arg in arguments:
            parser.add_argument("--" + arg[0], dest=arg[0], required=arg[1])

        args = parser.parse_args()

        return args

    @staticmethod
    def retry(max_retries=1, delay=1,exceptions: tuple=(Exception,), delay_type: str=DelayType.LINEAR, rate_limiter: RateLimiter=None):
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
    def parse_arguments(arguments):
        """Parse command line arguments required for the job.

        :param arguments: command line arguments. [('arg_name', is_required - boolean flag)]
        :return: list of commands line arguments
        """
        parser = argparse.ArgumentParser()
        for arg in arguments:
            parser.add_argument("--" + arg[0], dest=arg[0], required=arg[1])

        args = parser.parse_args()

        return args

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

    def trigger_in_spark_df_batches(self, func: Callable, dataframe, *args, **kwargs):

        if not self.total_len:
            if isinstance(dataframe, pd.DataFrame):
                self.total_len = len(dataframe)
            else:
                self.total_len = dataframe.count()
        message = ''

        self.start = self.end
        self.end = self.start + self.batch_size

        if self.end >= self.total_len:
            self.terminate = True
            self.end = self.total_len

        try:
            if isinstance(dataframe, pd.DataFrame):
                df_batch = dataframe.iloc[self.start:self.end]
            else:
                df_batch = dataframe.limit(self.end - self.start)
            self.df_batch_rows = df_batch.count()
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
                self.trigger_in_spark_df_batches(func, dataframe, *args, **kwargs)

    def trigger_in_list_batches(self, func: Callable, data_list, *args, **kwargs):

        if not self.total_len:
            self.total_len = len(data_list)
        message = ''

        self.start = self.end
        self.end = self.start + self.batch_size

        if self.end >= self.total_len:
            self.terminate = True
            self.end = self.total_len

        try:
            data_list_batch = data_list[self.start:self.end]
            self.df_batch_rows = len(data_list_batch)
            logging.info(f"function: {func.__name__} | start: {self.start} | end: {self.end} | batch_size: {self.df_batch_rows}")
            message = func(data_list=data_list_batch, *args, **kwargs)
            status = "success"
        except Exception as e:
            message = f"{type(e).__name__}:{e}"
            status = "error"
        finally:
            batch_log = self.batch_log(status=status, message=message)
            logging.info(batch_log)

            if not self.terminate:
                self.trigger_in_list_batches(func, data_list, *args, **kwargs)