import json
import requests
from martech_sdk.utils import logging
from martech_sdk.operators.gcp.secret_manager import SecretManagerOperator
from martech_sdk.configs.env import EnvConfig
import os

class VaultOperator:

    TOKEN_URL_TEMPLATE = "https://<SERVER>/v1/auth/<PROJECT_PATH_NAME>/login"
    SECRETS_PATH_TEMPLATE = "https://<SERVER>/v1/secrets/data/<PROJECT_PATH_NAME>/<SECRET_PATH>"

    @classmethod
    def get_token(cls):

        logging.info("Fetching Vault token.")
        role_id, secret_id = SecretManagerOperator().get()

        data = {
            "role_id": role_id,
            "secret_id": secret_id
        }

        headers = {
            "Content-Type": "application/json"
        }

        url = cls.TOKEN_URL_TEMPLATE.replace("<SERVER>", EnvConfig.VAULT.SERVER).replace("<PROJECT_PATH_NAME>", EnvConfig.VAULT.MARTECH_PATH_NAME)

        logging.info(f"URL : {url}")
        logging.info(f"Data : {data}")
        logging.info(f"Headers : {headers}" )

        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            logging.info("Vault Token generated.")
            logging.info("Vault token fetched from secret manager.")

            return response.json()['auth']['client_token']
        else:
            logging.info("get_token Request failed.")
            logging.info(f"Status code: {response.status_code}")
            logging.info(f"Response: {response.text}")
            return None

    @classmethod
    def get_secret(cls, secret_path: str):

        logging.info("Fetching secrets from vault.")
        token = cls.get_token()

        url_base = (
            cls.SECRETS_PATH_TEMPLATE.replace("<SERVER>", EnvConfig.VAULT.SERVER)
            .replace("<PROJECT_PATH_NAME>", EnvConfig.VAULT.MARTECH_PATH_NAME)
        )

        url = os.path.join(url_base, secret_path)

        headers = {
            "X-Vault-Token": token,
            "Content-Type": "application/json"
        }

        logging.info(f"URL : {url}")
        logging.info(f"Headers : {headers}")

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logging.info("Secrets Fetched from vault.")
            return response.json()['data']['data']
        else:
            logging.info("get_secret Request failed.")
            logging.info(f"Status code: {response.status_code}")
            logging.info(f"Response: {response.text}")
            return None