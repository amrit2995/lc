import requests
import os
import subprocess
from martech_sdk.utils import logging
from martech_sdk.configs.nucleus import NUCLEUS_CONFIG
from martech_sdk.utils.adapter import Adapter

class Nucleus:
    """Fetches certs and config from Nucleus
        Args::
            env
            applicationName
            scope
            nucleusHash
    """

    @staticmethod
    def get(env, applicationName='', scope='', nucleusHash='', region='east'):

        try:

            env = Adapter.env(env=env, service='Nucleus')

            if region not in NUCLEUS_CONFIG['host'].keys():
                raise ValueError(f"Invalid regoin provided: {region}")

            getConfigurationApi = (
                (NUCLEUS_CONFIG['host'][region][env] + NUCLEUS_CONFIG['uri']['getConfig']).replace('{applicationName}',applicationName)
                .replace('{scopeName}',scope)
            )
            
            logging.info(f"getConfigurationApi : {getConfigurationApi}")

            headers = {
                "Authorization":nucleusHash
            }

            logging.info(f"headers : {headers}")

            response = requests.get(url=getConfigurationApi, headers=headers, timeout=10)
            response_status = response.status_code
            if response_status not in (200, 202):
                raise requests.exceptions.RequestException(f'Status code: {response_status}, Error:{response.reason}, Response: {response.text}')
            logging.info(f"Response Status : {response_status}")
            logging.info("Response from Nucleus fetched successfully")
            response = response.json()
            return response
        except Exception as e:
            logging.error(f"{type(e).__name__}:{e}")
            logging.error("Failed to Fetch from Nucleus.")

    @staticmethod
    def _createCredsFile(
        data,
        file_name: str='test.json',
        base_path=None,
        permission_code=None,
        env='all',
        applicationName='martech-media-market-gcp',
        scope='general'
        ):

        base_path = base_path if base_path else os.getcwd()
        filePath = os.path.join(base_path, 'certs',f"{env}_{applicationName}_{scope}_{file_name}")
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
    def update(env, applicationName='', scope='', nucleusHash='', region='east'):

        env = Adapter.env(env=env, service='Nucleus')

        get_original_data = Nucleus.get(env=env, applicationName=applicationName, scope=scope, nucleusHash=nucleusHash, region=region)

        if region not in NUCLEUS_CONFIG['host'].keys():
            raise ValueError(f"Invalid regoin provided: {region}")

        getConfigurationApi = (
            (NUCLEUS_CONFIG['host'][region][env] + NUCLEUS_CONFIG['uri']['getConfig']).replace('{applicationName}',applicationName)
            .replace('{scopeName}',scope)
        )
        
        logging.info(f"getConfigurationApi : {getConfigurationApi}")

        headers = {
            "Authorization":nucleusHash
        }

        logging.info(f"headers : {headers}")