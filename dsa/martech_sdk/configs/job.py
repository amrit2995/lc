# from os import getcwd
from martech_sdk.configs.env import EnvConfig
# from martech_sdk.operators.gcp.storage import StorageOperator
import os
import json
from martech_sdk.utils import logging

############################################# Enums #############################################

class ConfigSource:
    GCS = "gcs"
    LOCAL = "local"
    NUCLEUS = "nucleus"
    FILE_PATH = "file_path "

class Vendor:
    PINTEREST = "pinterest"
    META = "meta"
    GOOGLE_ADS = "google_ads"
    YANDEX = "yandex"


############################################# Job Config  ########################################
class JobConfigs:
    
    ENV = EnvConfig.ENV
    BUCKET = EnvConfig.BUCKET.SOURCE
    

    # def download_from_gcs(self):

    #     config_path = ""
    #     StorageOperator.download_file(source=source, destination=os.getcwd(), bucket_name=self.BUCKET)

    @classmethod
    def load_json_config(cls, config_name: str, source=ConfigSource.LOCAL, base_path: str=''):

        logging.info("Loading channels Configs.")
        try:
            if source == ConfigSource.LOCAL:
                config_file_name  = f"{config_name}-{cls.ENV}.json"
                config_file_path = os.path.join(base_path, config_file_name)
                logging.info(f"Config File Path:- {config_file_path}")

                with open(config_file_path, "r") as f:
                    config = json.load(f)

                config = config["channel"]
                
                logging.info(f"Load config :- {config}")
            return config
        except Exception as e:
            logging.error(f"{type(e).__name__}:{e}")
            raise