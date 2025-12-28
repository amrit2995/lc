import requests
from delta_sdk.utils import logging
from delta_sdk.configs.nucleus import NUCLEUS
from delta_sdk.utils.adapter import Adapter

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
            env = Adapter.env(env=env, applicationName=applicationName, scope=scope)

            if region not in NUCLEUS['host'].keys():
                raise ValueError(f"Invalid regoin provided: {region}")

            getConfigurationApi = (
                (NUCLEUS['host'][region][env] + NUCLEUS['uri']['getConfig']).replace('{applicationName}',applicationName)
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