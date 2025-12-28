from martech_sdk.operators import BaseOperator
from martech_sdk.utils import logging
import json
from martech_sdk.operators.vault import VaultOperator


class GAMOperator(BaseOperator):
    
    VAULT_SECRET_PATH = 'martech/onprem/turbo_titans/common/gam'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_certs(self, vault_secret_path: str = VAULT_SECRET_PATH):
        logging.info("Fetching GAM secrets from vault.")
        vault_secret_data = VaultOperator.get_secret(secret_path=vault_secret_path)
        
        meta_secret_raw = vault_secret_data['meta_secrets']
        meta_secret_clean = meta_secret_raw.replace('\n', '').replace('\xa0', '')
        json_payload = json.loads(meta_secret_clean)
        access_token = json_payload.get('access_token')
        logging.info("GAM secrets fetched from vault.")

        return access_token