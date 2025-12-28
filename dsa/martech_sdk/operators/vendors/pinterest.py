from martech_sdk.utils import logging
from martech_sdk.operators import BaseOperator
import requests
from martech_sdk.configs.env import EnvConfig
from martech_sdk.configs.accounts import LMNAccount, EnterpriseAccount
from martech_sdk.operators.gcp.storage import StorageOperator
from martech_sdk.utils.nucleus import Nucleus
import time
import json
import os
import csv
import io

class DestinationType:
    LOCAL = 'local'
    GCS = 'gcs'

class PinterestCreds:
    def __init__(self, refresh_token='', client_auth=''):
        self.refresh_token = refresh_token
        self.client_auth = client_auth

class PinterestOperator(BaseOperator):

    SERVER_URL = "https://api.pinterest.com/"
    ACCESS_TOKEN_ENDPOINT = "v5/oauth/token"
    CAMPAIGN_METADATA_ENDPOINT = "v5/ad_accounts/<account_id>/campaigns"
    CAMPAIGN_METRICS_ENDPOINT = "v5/ad_accounts/<account_id>/campaigns/<campaign_id>/reports"
    CAMPAIGN_METRICS_REPORT_ENDPOINT = "v5/ad_accounts/<account_id>/reports"

    def __init__(
        self,
        env,
        account_type: str = EnterpriseAccount.ACCOUNT_TYPE,
        nucleus_hash: str = None,
    ):
        if account_type == LMNAccount.ACCOUNT_TYPE:
            self.account_id = LMNAccount.PINTEREST_ID
        elif account_type == EnterpriseAccount.ACCOUNT_TYPE:
            self.account_id = EnterpriseAccount.PINTEREST_ID
        else:
            logging.info("Invalid account type.")
            return None

        self.env = env
        self.account_type = account_type
        self.nucleus_hash = nucleus_hash
        self._refresh_token = None
        self._access_token = None
        self.creds = None
    
    @property
    def refresh_token(self):
        if not self._refresh_token:
            self._refresh_token = self.get_refresh_token()
        return self._refresh_token

    @property
    def access_token(self):
        client_auth = self.get_client_auth_base64()
        if not self._access_token:
            self._access_token = self.get_access_token(
                refresh_token=self.refresh_token,
                client_auth=client_auth
                )
        return self._access_token

    def fetch_pinterest_creds_from_nucleus(self):
        
        application_name = 'martech-media-market-gcp'
        scope = 'pinterest'

        if not self.creds:
            response_data = Nucleus.get(env=self.env, applicationName=application_name, scope=scope, nucleusHash=self.nucleus_hash)['data']

            self.creds = PinterestCreds(
                refresh_token=response_data.get('refresh_token'),
                client_auth=response_data.get('client_auth_base64')
                )

        return self.creds

    def get_refresh_token(self):
        return self.fetch_pinterest_creds_from_nucleus().refresh_token

    def get_client_auth_base64(self):
        return self.fetch_pinterest_creds_from_nucleus().client_auth

    def get_access_token(self, client_auth, refresh_token):
        logging.info("Generating Pinterest Access Token.")
        url = self.SERVER_URL + self.ACCESS_TOKEN_ENDPOINT

        headers = {
        'Authorization': f'Basic {client_auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Keep payload as raw string to avoid encoding mismatches
        payload = (
            f"grant_type=refresh_token"
            f"&refresh_token={refresh_token}"
            f"&scope=ads%3Aread%2Cboards%3Aread%2Cpins%3Aread"
        )

        logging.info(f"URL: {url}")
        logging.info(f"HEADERS: {headers}")
        logging.info(f"PAYLOAD: {payload}")

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            logging.info("Access Token Fetched from Pinterest.")
            return response.json().get("access_token")
        else:
            logging.error("get_access_token Request failed.")
            logging.error(f"Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return None

    def fetch_campaign_metadata(self, campaign_ids: list, page_size: int = 250):

        url = self.SERVER_URL + self.CAMPAIGN_METADATA_ENDPOINT.replace("<account_id>", self.account_id)

        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        campaign_ids_str = ",".join(campaign_ids)

        params = {
            "page_size": page_size,
            "campaign_ids": campaign_ids_str
        }

        logging.info(f"URL: {url}")
        logging.info(f"HEADERS: {headers}")
        logging.info(f"PARAMS: {params}")

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            logging.info("Campaign Metadata Fetched from Pinterest.")
            items_list = response.json().get("items")
            logging.info(f"Campaigns details len: {len(items_list)}")
            return response.json().get("items")
        else:
            logging.info("get_campaign_metadata Request failed.")
            logging.info(f"Status code: {response.status_code}")
            logging.info(f"Response: {response.text}")
            return None

    def chunk_list(self, lst, n):
        """Yield successive n-sized chunks from a list."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def fetch_campaign_metadata_in_chunks(self, campaign_ids: list, page_size: int = 250, chunk_size: int = 90):

        """
        Fetch campaign metadata in batches of given size and merge results.
        """
        all_items = []

        for chunk in self.chunk_list(campaign_ids, chunk_size):
            logging.info(f"Fetching batch of {len(chunk)} campaigns")
            batch_items = self.fetch_campaign_metadata(chunk, page_size)
            all_items.extend(batch_items)

        logging.info(f"Total Campaigns fetched: {len(all_items)}")
        return all_items if all_items else None

    @staticmethod
    def pinterest_report_retry(max_retries=1, delay=1,exceptions: tuple=(Exception,)):
        """
            Args::
                max_retries | optional
                delay | Optional
                exceptions | Optional | By default Retries for any Exception.

        """
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                retries_left = max_retries
                nonlocal delay
                while retries_left >0:
                    try:
                        response = func(*args, **kwargs)
                        if response.status_code == 200:
                            report_status = response.json().get("report_status")
                            if report_status == "FINISHED":
                                logging.info("Report is ready.")
                                return response.json()["token"]
                            elif report_status == "IN_PROGRESS":
                                logging.info(
                                    f"Report status is 'IN_PROGRESS'. Retrying in {delay} seconds..."
                                    f"Report is not ready with status code: {report_status}"
                                    )
                            else:
                                logging.info(f"Report generation not finished.Report Status:- {report_status}")
                        else:
                            raise Exception(f"Request failed with status code: {response.status_code}")
                    except exceptions as e:
                        retries_left -= 1
                        logging.error(f"{type(e).__name__}:{e}")
                        logging.info(f"Retries left : {retries_left} | Delaying for {str(delay)} sec")
                        time.sleep(delay)

                raise RuntimeError(f"Falied after {max_retries} attempts")
            return inner_wrapper
        return wrapper

    @pinterest_report_retry(max_retries=5, delay=5)
    def generate_report_token(self, data, access_token):

        URL = self.SERVER_URL + self.CAMPAIGN_METRICS_REPORT_ENDPOINT.replace("<account_id>", self.account_id)


        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json"
        }

        payload = json.dumps(data)

        logging.info(f"URL: {URL}")
        logging.info(f"HEADERS: {headers}")
        logging.info(f"DATA: {payload}")
        response = requests.post(URL, headers=headers, data=payload)
        logging.info(f'Report Fetched: {response}')
        return response
    
    def fetch_report_url(self, access_token, report_token):

        logging.info("Fetch Report.")
        URL = self.SERVER_URL + self.CAMPAIGN_METRICS_REPORT_ENDPOINT.replace("<account_id>", self.account_id)

        if not access_token:
            access_token = self.access_token

        headers = {
            "Authorization": "Bearer " + access_token,
        }

        params = {
            "token": report_token
        }

        logging.info(f"URL: {URL}")
        logging.info(f"HEADERS: {headers}")
        logging.info(f"PARAMS: {params}")

        response = requests.get(URL, headers=headers, params=params)

        data = response.json()
        size = data.get("size")
        url = data.get("url")
        logging.info(f'Report Fetched: {response}')
        logging.info(f"Report Size: {size}")
        logging.info(f"Report URL: {url}")

        return url

    @classmethod
    def download_report(cls, report_url: str, download_path=''):
        try:
            logging.info(f"Download Report.")
            response: requests.Response = requests.get(report_url, stream=True)
            logging.info(f"Response: {response}")
            if response.status_code != 200:
                raise Exception(f"Failed to download file. HTTP Status: {response.status_code}")
            
            if not download_path:
                download_path = os.getcwd()

            local_path = os.path.join(os.getcwd(), "report.csv")
            logging.info(f"Local Path: {local_path}")
            # logging.info(f"Destination Type: {dest}")

            with open(local_path, "w", newline="") as f:
                reader = csv.reader(io.StringIO(response.content.decode("utf-8")))
                writer = csv.writer(f)
                writer.writerows(reader)

            # if dest == 'gcs':
            #     logging.info(f"Upload to GCS: {download_path}")
            #     StorageOperator.upload_file(source=local_path, destination=download_path)

            return local_path
        except Exception as e:
            logging.error(f"Failed to download file. Error: {e}")
            raise

    def fetch_report(
            self, 
            data: dict, 
            access_token: str='', 
            download_path='',
            ):

        report_token = self.generate_report_token(data=data, access_token=access_token)
        logging.info(f"Report Token: {report_token}")
        report_url = self.fetch_report_url(access_token=access_token, report_token=report_token)
        download_path = self.download_report(report_url=report_url, download_path=download_path)
        logging.info("Report Fetched.")
        return download_path