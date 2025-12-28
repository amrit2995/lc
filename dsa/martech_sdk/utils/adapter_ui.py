import sys
from martech_sdk.configs.env import EnvConfig
from martech_sdk.configs.common import CommonConfigs
from martech_sdk.utils import logging
from martech_sdk.operators.gcp.storage import StorageOperator
from martech_sdk.utils.common import CommonUtils, BatchExec
from martech_sdk.utils.nucleus import Nucleus
from pyspark.sql import DataFrame

import requests
import pandas as pd

class CertSource:
    GCS = "gcs"
    LOCAL = "local"
    NUCLEUS = "nucleus"

class DataType:
    DATAFRAME = "dataframe"
    LIST = "list"
    DICT = "dict"

class AdapterUICreds:

    def __init__(self, env, cert=None, server=None, gcs_certs_file_path=None):
        logging.info("Initializing AdapterUICreds...")
        self.env = env
        self.cert = cert
        self.server = server
        self.gcs_certs_file_path = gcs_certs_file_path
        logging.info("AdapterUICreds initialized successfully.")

    # def __call__(self, key=None):
    #     if hasattr(self, key):
    #         return getattr(self, key)
    #     return {'host': self.server, 'ca_path': self.cert}

    # def __repr__(self):
    #     return f"AdapterUICreds(server={self.server}, ca_path={self.cert})"
    

class AdapterUI:

    ANALYTICS_MEASUREMENT_API = "/marketing-dashboard-api/adapters/write-analytics-measurement"
    MARKETING_DASHBOARD_API = "/marketing-dashboard-api/adapters/write-marketing-dashboard"


    def __init__(
        self,
        env,
        creds_source=CertSource.NUCLEUS,
        nucleus_hash=None
        ):
        logging.info("Initializing AdapterUI...")
        self.env = env
        self.creds_source = creds_source
        self.nucleus_hash = nucleus_hash
        self.creds = None
        logging.info("AdapterUI initialized successfully.")

    def _fetch_creds_from_nucleus(self):
        """
        Fetch the creds file from Nucleus and return the local path.
        """
        logging.info("Fetching the creds file from Nucleus...")
        application_name = "martech-media-market-gcp"
        scope = "adapter-ui"

        if not self.creds:
            data = Nucleus.get(env=self.env, applicationName=application_name, scope=scope, nucleusHash=self.nucleus_hash)['data']
            self.creds: AdapterUICreds = AdapterUICreds(
                env=self.env, 
                cert=data.get('cert'), 
                server=data.get('server'), 
                gcs_certs_file_path=data.get('gcs_certs_file_path')
                )
        logging.info("Fetched creds from Nucleus.")

        return self.creds

    @property
    def server(self):
        return self._fetch_creds_from_nucleus().server

    @property
    def cert(self):
        return self._fetch_creds_from_nucleus().cert

    @property
    def gcs_certs_file_path(self):
        return self._fetch_creds_from_nucleus().gcs_certs_file_path

    def generate_certs_file(self, source=CertSource.NUCLEUS):
        """
        Fetch the certs file from GCS and return the local path.
        """
        logging.info("Generating certs file...")
        if source == CertSource.NUCLEUS:
            creds = self._fetch_creds_from_nucleus()

            file_path = Nucleus._createCredsFile(
                data=creds.cert,
                file_name='adapter-ui.pem',
                permission_code="600",
                env=self.env,
                applicationName='martech-media-market-gcp',
                scope='adapter-ui'
            )
            return file_path

        elif source == CertSource.GCS and EnvConfig.ADAPTER_UI.GCS_CERTS_FILE_PATH:
            dest_path = StorageOperator.download_file(
                source=EnvConfig.ADAPTER_UI.GCS_CERTS_FILE_PATH,
                destination=EnvConfig.ADAPTER_UI.LOCAL_CERTS_FILE_PATH,
                bucket_name='daci-media-mrkt-temp-dev'
            )
            logging.info(f"Certs file downloaded successfully to {dest_path}")
            return dest_path
        else:
            logging.error("No GCS certs file path provided.")
            raise ValueError("No GCS certs file path provided.")

    @CommonUtils.retry(max_retries=3)
    def mesaurement_api(self, data_list: list, cert_source=CertSource.NUCLEUS):
        """
        Send the measurement data to the Adapter UI.
        """
        logging.info("Sending measurement data to Adapter UI...")
        url =  self.server + self.ANALYTICS_MEASUREMENT_API

        logging.info(f"URL : {url}")
        # logging.info(f"Data : {data_list}")
        cert_path = self.generate_certs_file(source=cert_source)

        headers = {
            "Content-Type": "application/text"
        }

        response = requests.put(url, json=data_list, verify=cert_path)

        logging.info(f"Status code: {response.status_code}")
        logging.info(f"Response: {response.text}")

        if response.status_code == 200:
            logging.info("Measurement data sent successfully.")
            return "success"
        else:
            logging.info("Measurement data sent failed.")
            return "error"

    def trigger_measurement_api_in_batches(self, data: list, batch_size= sys.maxsize):
        """
        Trigger the measurement api in batches.
        """
        logging.info("Triggering measurement api in batches...")
        batch_exec: BatchExec = BatchExec(batch_size=batch_size)
        batch_exec.trigger_in_list_batches(func=self.mesaurement_api, data_list=data)

        logging.info("Measurement data sent successfully.")
        return True

    @CommonUtils.retry(max_retries=3)
    def dashboard_api(self, data_list: list, cert_source=CertSource.NUCLEUS):
        """
        Send the dashboard data to the Adapter UI.
        """
        logging.info("Sending dashboard data to Adapter UI...")
        url =  self.server + self.MARKETING_DASHBOARD_API

        logging.info(f"URL : {url}")
        # logging.info(f"Data : {data_list}")
        cert_path = self.generate_certs_file(source=cert_source)

        headers = {
            "Content-Type": "application/text"
        }

        response = requests.put(url, json=data_list, verify=cert_path)

        logging.info(f"Status code: {response.status_code}")
        logging.info(f"Response: {response.text}")

        if response.status_code == 200:
            logging.info("Dashboard data sent successfully.")
            return "success"
        else:
            logging.info("Dashboard data sent failed.")
            return "error"