from delta_sdk.connectors.base import BaseConnector
from delta_sdk.configs.connConfigs import MINIO
from minio import Minio
import urllib3
from minio.error import S3Error
from delta_sdk.utils import logging
from delta_sdk.utils.common import CommonUtils


class MinioConnector(BaseConnector):
    def __init__(self, 
                env: str = '',
                nucleusHash: str ='',
                base_path: str='',
                region: str='east'):
        super().__init__(env=env, applicationName=MINIO["applicationName"][env], scope=MINIO["scope"][env],
                          nucleusHash=nucleusHash, base_path=base_path, region=region)
        self._client = None

    @CommonUtils.retry_connection(max_retries=1, delay=1)
    def get_minio_creds(self):
        data = self.get_creds()
        cert_path = self._createCredsFile(data=data['ca'], file_name="minioFile.pem")
        host = data["MINIO_API_HOST"].split("://",1)[1]
        access_key=data["ACCESS_KEY"]
        secret_key=data["SECRET_KEY"]
        return [host, access_key, secret_key, cert_path]

    @property
    @CommonUtils.retry_connection(max_retries=1, delay=1)
    def client(self):
        host, access_key, secret_key, cert_path = self.get_minio_creds()
        connection = urllib3.PoolManager(cert_reqs="CERT_NONE", ca_certs=cert_path)

        if not self._client:
            self._client = Minio(
                endpoint=host,
                access_key=access_key,
                secret_key=secret_key,
                secure=True,
                http_client=connection
            )
        return self._client
    
    def download(self, source='', destination='', bucket_name=''):
        try:
            logging.info(f"Download from source: {source} to destination: {destination}")
            result = self.client.fget_object(bucket_name=bucket_name, object_name=source, file_path=destination)
            logging.info(f"result: {result}")
        except S3Error as err:
            logging.info(f"Error: {err}")

    def upload(self, source='', destination='', bucket_name=''):
        try:
            logging.info(f"Download from source: {source} to destination: {destination}")
            result = self.client.fput_object(bucket_name, object_name=destination, file_path=source)
            logging.info(f"result: {result}")
        except S3Error as err:
            logging.info(f"Error: {err}")