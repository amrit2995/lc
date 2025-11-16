import json
import time
import os
import logging
from pytz import timezone
from datetime import datetime
from config.configs import COMMON_CONFIG
from core.logging_tracing import setup_logger,setup_tracing
# Initialize logging and tracing
setup_logger()
setup_tracing()
logger = logging.getLogger(__name__)



class UtilityClass:

    @staticmethod
    def getCurrentTS():
        tz = timezone(COMMON_CONFIG["TIMEZONE_CONFIG"])
        local_time = datetime.now(tz)
        return local_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def time_calculator(func):
        def wrapper(*args, **kwargs):
            fname = func.__name__
            UtilityClass.handleInfoLogs(f"Function currently running : {fname}")
            start_time = time.time()
            output = func(*args, **kwargs)
            end_time = time.time()
            UtilityClass.handleInfoLogs(f" {fname} Total Time Taken : {end_time - start_time}")
            return output
        return wrapper
   

    @staticmethod
    def _createTempFile(file_name: str='test.json'):
        filePath = os.path.join(os.getcwd(), 'temp',f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{file_name}")

        # Ensure the directory structure exists (create if necessary)
        os.makedirs(os.path.dirname(filePath), exist_ok=True)

        return filePath
    
    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except (IOError, json.JSONDecodeError) as e:
            UtilityClass.handleInfoLogs(f"Failed to read from {file_path}: {e}")
            return {}

    @staticmethod
    def compare_two_dates(date_str1,date_str2):
        date1 = datetime.strptime(date_str1, "%Y-%m-%dT%H:%M:%S.%fZ")
        date2 = datetime.strptime(date_str2, "%Y-%m-%dT%H:%M:%S.%fZ")
        if date1 >= date2:
            return True
        else:
            return False

    @staticmethod
    def handleErrorLogs(*logLine):
        logs_str = ' '.join(str(arg) for arg in logLine)
        logger.error(logs_str)
    
    @staticmethod
    def handleInfoLogs(*logLine):
        logs_str = ' '.join(str(arg) for arg in logLine)
        logger.info(logs_str)
