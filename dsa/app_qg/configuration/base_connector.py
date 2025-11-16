import os
import time
import json
from helpers.common import UtilityClass
from helpers.nucleus import Nucleus

class BaseConnector:
    env: str
    applicationName: str
    scope: str
    nucleusHash: str
    base_path: str

    def __init__(self, 
                env: str ='',
                scope: str ='', 
                applicationName: str ='', 
                nucleusHash: str ='',
                base_path: str=''):
        self.env = env
        self.scope = scope
        self.applicationName = applicationName
        self.nucleusHash = nucleusHash
        self.base_path = base_path if base_path else os.getcwd()
        self.gcs_secret_file_name = 'gcs_secret.pem'

    def _valid_param(self, param):
        val = getattr(self, param, None)
        return val and isinstance(val, str)


    def get_creds(self):

        required_params = ['env', 'applicationName', 'scope', 'nucleusHash']
        if all([self._valid_param(param) for param in required_params]):
            response =  Nucleus.get(env=self.env, applicationName=self.applicationName, scope=self.scope, nucleusHash=self.nucleusHash)
            return response.get('data')


    def get_gcs_creds(self):
        data = self.get_creds()
        return self._createCredsFile(data=json.dumps(data), file_name=self.gcs_secret_file_name)
        

    def _createCredsFile(self, data, file_name: str='test.json'):
        filePath = os.path.join('certs',f"{self.applicationName}_{self.scope}_{file_name}")

        # Ensure the directory structure exists (create if necessary)
        os.makedirs(os.path.dirname(filePath), exist_ok=True)

        # Open the file in write mode (overwrites if it exists)
        with open(filePath, "w") as file:
            file.write(data)
        return filePath

    @staticmethod
    def retry_connection(max_retries=1, delay=1,exceptions=(Exception,)):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                retries_left = max_retries
                while retries_left >0:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        retries_left -= 1
                        UtilityClass.handleErrorLogs(f"Exception: {e}, Retries left : {retries_left}")
                        time.sleep(delay)
                raise RuntimeError(f"Falied after {max_retries} attempts")
            return inner_wrapper
        return wrapper