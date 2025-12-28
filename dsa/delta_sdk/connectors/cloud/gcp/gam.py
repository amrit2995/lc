from delta_sdk.connectors.base import BaseConnector
from delta_sdk.configs.connConfigs import GAM
from googleads import ad_manager
from delta_sdk.utils import logging
import yaml
import importlib.resources as pkg_resources
from delta_sdk import configs
from delta_sdk.utils.common import CommonUtils

class GAMConnector(BaseConnector):
    def __init__(self, 
                env: str = '',
                nucleusHash: str ='',
                base_path: str='',
                region: str='east'
                ):

        logging.info(f"Setting connector for env:- {env}")
        self.gcp = True

        super().__init__(env=env, applicationName=GAM["applicationName"][env], scope=GAM["scope"][env],
                          nucleusHash=nucleusHash, base_path=base_path, region=region)
        self._client = None

    @CommonUtils.retry_connection(max_retries=1, delay=1)
    def get_client(self, yaml_config=''):

        if not self._client:

            if not yaml_config:
                logging.info("'yaml_config' not provided . Generating the GAM client with default googads template.")
                with pkg_resources.open_text(configs, "googleads.yml") as file:
                    yaml_config = yaml.load(file, Loader=yaml.SafeLoader)
                gcs_cred_file_path = self.get_gcs_creds(file_path=True)
                yaml_config['ad_manager']['path_to_private_key_file'] = yaml_config['ad_manager']['path_to_private_key_file'].replace('<google_creds_file_path>', gcs_cred_file_path)
            
            client = ad_manager.AdManagerClient.LoadFromString(yaml_doc=yaml.dump(data=yaml_config))
            self._client = client

        logging.info("GAM client successfully created.")
        return self._client