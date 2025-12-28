from martech_sdk.utils import logging
from martech_sdk.operators import BaseOperator
from martech_sdk.operators.vault import VaultOperator
import requests
import json
from martech_sdk.configs.env import EnvConfig

class MetaOperator(BaseOperator):

    def get_access_token(self):

        logging.info("Fetching Meta secrets from vault.")
        vault_secret_data = VaultOperator.get_secret(secret_path=EnvConfig.VENDOR.META.VAULT_SECRET_PATH)
        logging.info("Meta secrets fetched from vault.")
        meta_secret_raw = vault_secret_data['meta_secrets']
        meta_secret_clean = meta_secret_raw.replace('\n', '').replace('\xa0', '')
        json_payload = json.loads(meta_secret_clean)
        access_token = json_payload.get('access_token')
        logging.info("Meta access token fetched from vault.")

        return access_token