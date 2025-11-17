import re
import ast
import json
import time
import os
import copy
import logging
import requests
import numpy as np
from pytz import timezone
from datetime import datetime
from config.appConfigs import COMMON_CONFIG
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

    @staticmethod
    def to_bool(value):
        # If the value is already a boolean, return it directly
        if isinstance(value, bool):
            return value
        
        # Convert the value to a boolean if it's a string
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ['true', '1', 'yes', 'y']:
                return True
            elif value_lower in ['false', '0', 'no', 'n']:
                return False
        
        # If the value can't be converted, raise an error or return a default
        raise ValueError(f"Cannot convert {value} to boolean")
    @staticmethod
    def validate_array(arr):
        if arr is None:
            return False
        
        if not isinstance(arr, list):
            return False

        # Check if the array is not empty
        if len(arr) == 0:
            return False
        return True
    
    @staticmethod
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
    def remove_departmentNumber(input_string):
        return re.sub(r'^\d+/', '', input_string)
    @staticmethod
    def remove_after_last_character(input_string,ch):
    # Find the index of the last '/'
        last_slash_index = input_string.rfind(ch)
        
        # If '/' is found, slice the string up to and including the last '/'
        if last_slash_index != -1:
            return input_string[:last_slash_index]
        else:
            # Return the original string if '/' is not found
            return input_string
    
    @staticmethod
    def count_words(input_string):
        # Split the string into words based on whitespace
        words = input_string.split()
        # Return the number of words
        return len(words)
    
    @staticmethod
    def normalize_value(original_value, original_min, original_max, scaled_min, scaled_max):
        # Check to avoid division by zero if original_min == original_max
        if original_max == original_min:
            raise ValueError("Original Min and Original Max cannot be the same.")
        
        # Normalize the original value to the new scale
        normalized_value = ((original_value - original_min) / (original_max - original_min)) * (scaled_max - scaled_min) + scaled_min
        return normalized_value
    @staticmethod
    def calculate_cosine_similarity(vec1, vec2):
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        # Compute the dot product of vec1 and vec2
        dot_product = np.dot(vec1, vec2)

        # Compute the magnitudes of vec1 and vec2
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)

        # Compute the cosine similarity
        if norm_vec1 == 0 or norm_vec2 == 0:
            # Handle division by zero if any vector is zero
            score = 0.0
        else:
            score =  dot_product / (norm_vec1 * norm_vec2)
        
        min_new = COMMON_CONFIG["COSINE_SIMILARITY_MIN_RANGE"]
        min_old = -1
        max_new = COMMON_CONFIG["COSINE_SIMILARITY_MAX_RANGE"]
        max_old = 1

        score = float(score)
        cosineSimilarityScore  = {
            "score" : score,
            "normalizedScore" : min_new + ((score - min_old) * (max_new - min_new)) / (max_old - min_old)
        }
        return cosineSimilarityScore


    @staticmethod
    def write_file(file_path, data):
        try:
            with open(file_path, 'w') as file:
                file.write(data)
        except IOError as e:
            UtilityClass.handleErrorLogs(f"Failed to write to {file_path}: {e}")
    
    @staticmethod
    def write_missing_docs_to_file(file_path, missing_docs):
        try:
            with open(file_path, 'a') as file:
                
                for doc in missing_docs:
                    file.write(str(doc) + '\n')
        except IOError as e:
            UtilityClass.handleErrorLogs(f"Failed to write to {file_path}: {e}")
                

    @staticmethod
    def _createTempFile(file_name: str='test.json'):
        
        filePath = os.path.join('temp',file_name)
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
    def delete_file(file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                UtilityClass.handleInfoLogs(f"File '{file_path}' deleted successfully.")
                return True
            except PermissionError:
                UtilityClass.handleErrorLogs(f"Permission denied to delete '{file_path}'.")
                return False
            except Exception as e:
                UtilityClass.handleErrorLogs(f"An error occurred while deleting the file: {e}")
                return False
        else:
            UtilityClass.handleErrorLogs(f"File '{file_path}' does not exist.")
            return False

    @staticmethod
    def compare_two_dates(date_str1,date_str2):
        date1 = datetime.strptime(date_str1, "%Y-%m-%dT%H:%M:%S.%fZ")
        date2 = datetime.strptime(date_str2, "%Y-%m-%dT%H:%M:%S.%fZ")
        if date1 >= date2:
            return True
        else:
            return False
    
    @staticmethod
    def is_surrounded_by_single_quotes(s):
        return s.strip().startswith("'") and s.endswith("'")
    
    @staticmethod
    def fetch_search_terms(text):
        parts = text.split("[", 1)
        finalTerms = []
    
        if len(parts) > 1:
            termsString = parts[1]
            
            index = termsString.find("]")
            if index > 0:
                termsString = termsString[:index]
            terms = termsString.split(",")
            finalTerms = [s.replace("'", "").strip() for s in terms if UtilityClass.is_surrounded_by_single_quotes(s)]
        
        finalTerms = list(set(finalTerms))
        return finalTerms
    
    @staticmethod
    def clean_search_term(input_string):
        cleaned_string = re.sub(r"[^\x00-\x7F]+", "", input_string) 
        cleaned_string = re.sub(r"\s+", " ", cleaned_string)
        cleaned_string = cleaned_string.strip(r"/\\")
        cleaned_string = cleaned_string.lower().strip()
        return cleaned_string
    

    @staticmethod
    def handleErrorLogs(*logLine):
        logs_str = ' '.join(str(arg) for arg in logLine)
        logger.error(logs_str)
    
    @staticmethod
    def handleInfoLogs(*logLine):
        logs_str = ' '.join(str(arg) for arg in logLine)
        logger.info(logs_str)

    @staticmethod
    def get_largest_by_starting_integer(items):
        sorted_items = sorted(items, key=lambda x: int(x.split('/')[0]), reverse=True)
        max_value = int(sorted_items[0].split('/')[0])
        return [item for item in sorted_items if int(item.split('/')[0]) == max_value]

    @staticmethod
    def read_file_to_array(filename):
        with open(filename, 'r') as file:
            # Read each line and strip any leading/trailing whitespace
            lines = file.readlines()
            # Convert each line into an integer and store it in a list
            array = [line.strip() for line in lines]
        return array

    @staticmethod
    def remove_last_slash_recursively(s):
        results = []
        while '/' in s:
            results.append(s)
            s = s.rsplit('/', 1)[0]
        if len(s) > 0:
            results.append(s)
        return results

    @staticmethod
    def handle_bulllet_point(string_array):
        try:
            actual_list = ast.literal_eval(string_array)
            bullet_string = "'" + "','".join(actual_list) + "'" 
            return bullet_string
        except (ValueError, SyntaxError):
            raise ValueError("Invalid string format. Could not convert to a list.")

    @staticmethod
    def element_exists(array, field, value):
        for element in array:
            # If the elements are dictionaries
            if isinstance(element, dict):
                if element.get(field) == value:
                    return True
            
            # If the elements are objects with attributes
            elif hasattr(element, field):
                if getattr(element, field) == value:
                    return True
        
        return False

    @staticmethod
    def get_category_threshold_config(category_thresholds,product):
        if product and UtilityClass.validate_array(product["departmentDepth"]):
            departmentDepth = copy.deepcopy(product["departmentDepth"])
            departmentDepth.reverse()
            for department in departmentDepth:
                leafCategory = UtilityClass.remove_departmentNumber(department).lower()
                if leafCategory in category_thresholds:
                    return category_thresholds[leafCategory]
               
        return category_thresholds["default"]
    
    @staticmethod
    def remove_duplicates(arr, key):
        seen = set()
        unique_items = []
        
        for item in arr:
            value = item.get(key)  # Access the value by key
            if value not in seen:
                unique_items.append(item)
                seen.add(value)
        
        return unique_items
    
    @staticmethod
    def sort_objects(array, key, reverse=False):
        return sorted(array, key=lambda obj: obj.get(key, 0), reverse=reverse)
    
    @staticmethod
    def create_pd_url(description,productId,brand):
        text = brand + " " +  description
        text = text.split('(', 1)[0].strip()
        text = re.sub(r'[^a-zA-Z0-9 -]', '', text)
        text = text.replace(' ', '-')
        text = re.sub(r'-+', '-', text)
        pdURL = COMMON_CONFIG["PD_HOST_PREFIX"] + text + "/" + productId
        
        return pdURL

    def post_object_to_url_with_retry(url, data, retries=3, delay=2):
        attempt = 0
        while attempt < retries:
            try:
                # Send a POST request with JSON data
                response = requests.post(url, json=data)
                
                # Check if the request was successful
                if response.status_code == 200:
                    UtilityClass.handleInfoLogs(f"Successfully posted data to {url}")
                    return response.json()  # Assuming the response contains JSON
                else:
                    UtilityClass.handleErrorLogs(f"Failed to post data. Status code: {response.status_code}")
                    return response.text  # Return the response text for further inspection
            except requests.exceptions.RequestException as e:
                UtilityClass.handleErrorLogs(f"Attempt {attempt + 1} failed: {e}")
                attempt += 1
                if attempt < retries:
                    UtilityClass.handleErrorLogs(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    UtilityClass.handleErrorLogs(f"All {retries} attempts failed.")
                    return None
