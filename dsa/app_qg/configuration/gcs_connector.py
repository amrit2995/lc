import datetime
from configuration.base_connector import BaseConnector
from helpers.common import UtilityClass
from google.cloud import storage
from config.configs import GCS
from google.oauth2 import service_account


class GCSClient(BaseConnector):
    def __init__(self, 
                env: str = '',
                nucleusHash: str =''):
        super().__init__(env=env, applicationName=GCS["applicationName"][env], scope=GCS["scope"][env],
                          nucleusHash=nucleusHash, base_path='')
        SAFilePath = self.get_gcs_creds()
        self.credentials = service_account.Credentials.from_service_account_file(SAFilePath)
        self.client = storage.Client(credentials=self.credentials)
        self.bucket_name = GCS["bucketName"][env]
        self.bucket = self.client.bucket(self.bucket_name)
    
    def get_client(self):
        if self.client is None:
            self.client = storage.Client(credentials=self.credentials)

        return self.client
    
    def get_bucket_name(self):
        if self.bucket_name is None:
            return None

        return self.bucket_name

    def upload_file(self, source_file_name, destination_blob_name):
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file_name)
            UtilityClass.handleInfoLogs(f"File {source_file_name} uploaded to {destination_blob_name}.")
            return destination_blob_name
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Failed to upload file: {e}")
            return None

    def download_file(self, source_blob_name, destination_file_name):
        try:
            blob = self.bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)
            UtilityClass.handleInfoLogs(f"File {source_blob_name} downloaded to {destination_file_name}.")
            return destination_file_name
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Failed to download file: {e}")
            return None
    

    def create_v4_presigned_url(self,file_name, expiration_seconds=15):
        blob = self.bucket.blob(file_name)

        expiration_time = datetime.timedelta(seconds=expiration_seconds)
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration_time,
            method="GET"
        )
        
        return url