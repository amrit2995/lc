import os
from delta_sdk.utils.nucleus import Nucleus
import json
from google.oauth2 import service_account
from delta_sdk.utils import logging
from delta_sdk.utils.common import CommonUtils
import google.auth.transport.requests
import subprocess

class DelayType:
    LINEAR = "linear"
    EXPONENTIAL = "exponential"

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
                base_path: str='',
                region: str='east'
                ):
        self.env = env
        self.scope = scope
        self.region = region
        self.applicationName = applicationName
        self.nucleusHash = nucleusHash
        self.base_path = base_path if base_path else os.getcwd()
        self._access_token = None

        logging.info(f"Fetching details for object in Nucleus for following :- env : {env} | scope : {scope} | applicationName : {applicationName}")

    def _get_value(self, data: dict, keys: list):
        """Returns the first matching key's value from data, case-insensitively."""
        lower_data = {k.lower(): v for k, v in data.items()}
        for key in keys:
            if key.lower() in lower_data:
                return lower_data[key.lower()]
        return None  # or raise ValueError(f"Missing required key from {keys}")

    def _valid_param(self, param):
        logging.info(f"Fetching param '{param}'")
        try:
            val = getattr(self, param, '')
            if val and isinstance(val, str):
                return True
        except Exception as e:
            logging.error(f"{type(e).__name__}: {e}")
            logging.error(f"param '{param}' either not provided or not valid.")
            return False

        raise ValueError(f"Required param '{param}':'{val}' not found")

    def gcp_only(func):
        """Decorator prevent gcp specific methods be used by non-gcp Connectors."""
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'gcp') and self.gcp:
                return func(self, *args, **kwargs)
            raise PermissionError(f"{func.__name__} is unavailable for non-gcp resource. Gcp flag is not True")

        return wrapper

    def get_creds(self) -> dict:
        logging.info('Starting to fetch creds.')
        required_params = ['env', 'applicationName', 'scope', 'nucleusHash']
        if not all([self._valid_param(param) for param in required_params]):
            raise ValueError("All necessary params either not provided not valid.")
        logging.info("All provided params are valid.")
        response =  Nucleus.get(env=self.env, applicationName=self.applicationName, scope=self.scope, nucleusHash=self.nucleusHash, region=self.region)
        if not response:
            raise RuntimeError("Nucleus Fetch failed. No response received.")
        return response.get('data')

    @gcp_only
    def get_gcs_creds(self, file_path=False):

        logging.info("Starting to fetch GCS Creds.")
        data = self.get_creds()
        SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
        # logging.info(f"Get data from get_creds: {data}")
        creds_data_dumped = json.dumps(data)
        # logging.info(f'creds_data_dumped: {creds_data_dumped}')
        SAFilePath = self._createCredsFile(data=creds_data_dumped, file_name="gcp_secret.pem")

        if file_path:
            logging.info(f"Returning SAFilePath: {SAFilePath}")
            return SAFilePath
        logging.info("Creating credentials object")
        credentials = service_account.Credentials.from_service_account_file(SAFilePath, scopes=SCOPES)
        logging.info(f"Credential object created successfully.{credentials}")

        return credentials

    @property
    def access_token(self):
        credentials = self.get_gcs_creds()

        if credentials.token and not credentials.expired:
            logging.info('Returning old token.')
            return credentials.token

        logging.info("Refreshing Token.")
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        # logging.info("Access Token:", credentials.token)
        logging.info(f"Expiry Time:- {credentials.expiry}")
        return credentials.token

    @gcp_only
    def _get_gcs_client(self):

        def client_creation_by_credentials_object():
            credentials = self.get_gcs_creds()
            return self.gcs_object.Client(credentials=credentials)

        def client_creation_by_export_secret():
            self.export_secret_to_os_variable()
            return self.gcs_object.Client()

        def client_creation_by_cred_path():
            credentials_path = self.get_gcs_creds(file_path=True)
            logging.info(f"Creds path: {credentials_path}")
            return self.gcs_object.Client.from_service_account_json(credentials_path)

        client_creation_strategies = [
            client_creation_by_credentials_object, 
            client_creation_by_export_secret, 
            client_creation_by_cred_path
            ]

        for client_creation in client_creation_strategies:

            try:
                logging.info(f"Trying to create client with : {client_creation.__name__}")
                return client_creation()
            except Exception as e:
                logging.error(f"Client creation failed with {client_creation.__name__} \n{type(e).__name__} : {e}")

        logging.critical("All client creation strategies failed.")
        raise RuntimeError("Failed to create client using all strategies.")

    @gcp_only
    def export_secret_to_os_variable(self):
        data = self.get_creds()
        SAFilePath = self._createCredsFile(data=json.dumps(data), file_name="gcp_secret.pem")
        logging.info("Exporting variable: 'GOOGLE_APPLICATION_CREDENTIALS' in env")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SAFilePath
        logging.info("Export successful")
        logging.info(f'path for GCP Creds is: {SAFilePath}')

    def _createCredsFile(self, data, file_name: str='test.json', permission_code=None):

        filePath = os.path.join(self.base_path, 'certs',f"{self.env}_{self.applicationName}_{self.scope}_{file_name}")
        logging.info(f"Creating file path.")

        os.makedirs(os.path.dirname(filePath), exist_ok=True)

        with open(filePath, "w") as file:
            file.write(data)
        logging.info(f"Creds file created at : {filePath}")

        if permission_code:
            subprocess.run(["chmod", permission_code, filePath], check=True)
            logging.info(f"Setting permissions to {str(permission_code)}")

        return filePath

    @staticmethod
    def retry_connection(max_retries=1, delay=1,exceptions: tuple=(Exception,), delay_type: str=DelayType.LINEAR):

        logging.warning(
                "'retry_connection' will soon be depricated from 'delta_sdk.connectors.base.BaseConnector' \n",
                "Get 'retry_connection' from 'delta_sdk.utils.common.CommonUtils' instead"
        )
        return CommonUtils.retry_connection(max_retries=max_retries, delay=delay, exceptions=exceptions, delay_type=delay_type)