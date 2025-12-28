from delta_sdk.connectors.base import BaseConnector
# from delta_sdk.config.gcs import GCS
from google.cloud import storage
import os
import json
from delta_sdk.configs.connConfigs import GCS, GCS_COMPOSER
import yaml
from delta_sdk.utils import logging
from io import BytesIO
import gzip
from delta_sdk.utils.common import parse_yaml_config_data
from delta_sdk.utils.common import CommonUtils


class GCSStorageConnector(BaseConnector):
    def __init__(self, 
                env: str,
                nucleusHash: str,
                base_path: str='',
                composer = False,
                region: str = 'east'):

        logging.info(f"Setting connector for env:- {env}")

        if composer:
            super().__init__(env=env, applicationName=GCS_COMPOSER["storage"]["applicationName"][env], scope=GCS_COMPOSER["storage"]["scope"][env],
                            nucleusHash=nucleusHash, base_path=base_path, region=region)
            self.bucket_name = GCS_COMPOSER["storage"]["bucketName"][env]
        else:
            super().__init__(env=env, applicationName=GCS["storage"]["applicationName"][env], scope=GCS["storage"]["scope"][env],
                            nucleusHash=nucleusHash, base_path=base_path, region=region)
            self.bucket_name = GCS["storage"]["bucketName"][env]
        self.gcp = True
        self.composer = composer
        self.env = env
        self._client = None
        self._bucket = None

    def composer_only(func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'composer') and self.composer:
                return func(self, *args, **kwargs)
            raise PermissionError(f"{func.__name__} is unavailable for non-gcp-composer resource. Composer flag is not true")
        return wrapper
    
    @property
    @CommonUtils.retry_connection(max_retries=1, delay=1)
    def client(self):
        if not self._client:
            self.gcs_object = storage
            self._client = self._get_gcs_client()
        return self._client

    @property
    def bucket(self):
        if not self._bucket:
            self._bucket = self.client.bucket(self.bucket_name)
        return self._bucket

    def download_file(self, source, destination, bucket_name=''):

        if bucket_name:
            bucket = self.client.bucket(bucket_name)
        else:
            bucket = self.bucket

        logging.info(f"Bucket: {bucket}")

        source = self.get_relative_path(source)
        blob = bucket.blob(source)
        blob.download_to_filename(destination)
        logging.info(f"File {source} downloaded to {destination}.")
        return True

    def upload_file(self, source, destination, bucket_name='', get_signed_url=False, expiration=604800, content_type=''):

        if bucket_name:
            bucket = self.client.bucket(bucket_name)
        else:
            bucket = self.bucket

        destination = self.get_relative_path(destination)
        blob = bucket.blob(destination)
        if not content_type:
            blob.upload_from_filename(source)
        else:
            blob.upload_from_filename(source, content_type=content_type)
        logging.info(f"File {source} uploaded to {destination}.")

        if get_signed_url:
            return self.get_signed_url(blob=blob, expiration=expiration)
        return True

    def list_files(self, prefix, bucket_name='', absolute_path=False, filter=''):
        try:
            if bucket_name:
                bucket = self.client.bucket(bucket_name)
            else:
                bucket = self.bucket
            
            blobs = bucket.list_blobs(prefix=prefix)
            filenames = [blob.name for blob in blobs]
            logging.info('Successfully fetched files list.')
            return filenames

        except Exception as e:
            logging.error(f"Faled: {e}")

    def get_signed_url(self,file_name='', blob=None, bucket_name='', expiration=604800): 

        if not blob:
            if not file_name:
                ValueError('Niether blob not file_name provided.')
            bucket = None
            if bucket_name:
                bucket = self.client.bucket(bucket_name)
            else:
                bucket = self.bucket

            file_name = self.get_relative_path(file_name)
            blob = bucket.blob(file_name)
            
        logging.info("Generating Signed URL")

        signed_url = blob.generate_signed_url(
            expiration=expiration,
            method='GET',
            version='v4'
        )
        return signed_url

    def move_file(self, source, destination ,bucket_name=''):

        if bucket_name:
            bucket = self.client.bucket(bucket_name)
        else:
            bucket = self.bucket

        source_blob = bucket.blob(source)
        bucket.copy_blob(source_blob, bucket, destination)
        source_blob.delete()
        logging.info(f'Blob {source} renamed to {destination}.')
        return destination
        
    def delete_file(self, file_path, bucket_name=''):
        try:
            if bucket_name:
                bucket = self.client.bucket(bucket_name)
            else:
                bucket = self.bucket

            blob = bucket.get_blob(file_path)
            blob.delete()
            logging.info(f"Deleted the file: {file_path}")

        except Exception as e:
            logging.error(f"Faled: {e}")

    def gzip_file(self, source, destination, bucket_name='', get_signed_url=False):
        try:
            if bucket_name:
                bucket = self.client.bucket(bucket_name)
            else:
                bucket = self.bucket
            source_blob = bucket.blob(source)

            logging.info("Download the content of the .txt file")
            txt_data = source_blob.download_as_bytes()

            logging.info("Use gzip to compress the content")    
            compressed_data = BytesIO()
            with gzip.GzipFile(fileobj=compressed_data, mode='wb') as gz_file:
                gz_file.write(txt_data)

            destination_blob = bucket.blob(destination)

            logging.info("Upload the compressed content")
            destination_blob.upload_from_string(compressed_data.getvalue(), content_type='application/gzip')

            if get_signed_url:
                return self.get_signed_url(blob=destination_blob)

            logging.info(f'File "{source}" compressed to "{destination}" in bucket "{bucket_name}".')

        except Exception as e:
            logging.error(f"Faled: {e}")

    def get_relative_path(self, file_path):
        return GCSStorageOperators.get_relative_path(file_path=file_path, bucket_name=self.bucket_name)  

    def get_absolute_gsutil_path(self,file_path, bucket_name=''):
        if not bucket_name:
            bucket_name = self.bucket_name
        return GCSStorageOperators.get_absolute_gsutil_path(file_path=file_path, bucket_name=bucket_name)
    
    def get_bucket_name(self, gcs_url=''):
        if gcs_url:
            return GCSStorageOperators.get_bucket_name(gcs_url=gcs_url)
        return self.bucket_name

    @composer_only
    def load_config_from_yaml(self, config_path):

        try:
            bucket = self.bucket
            blob = bucket.blob(config_path)
            logging.info("Successfully loaded config for the composer job.")
            config = parse_yaml_config_data(yaml_data=blob.download_as_bytes())
            return config
        except Exception as e:
            logging.info('load failed {}', e)
            return None
        
    def load_dataproc_cluster_config(self, dataproc_file_path='dataproc-essentials/dataproc_cluster_config.json'):
        dataproc_config= {}
        try:
            self.download_file(source=dataproc_file_path, destination='./dataproc_cluster_config.json')
            with open('./dataproc_cluster_config.json', "r") as config_file:
                dataproc_config = json.load(config_file)['dataproc_cluster']
            return dataproc_config
        except Exception as e:
            logging.info('load failed {}', e)
            return None
class GCSStorageOperators:
    
    @staticmethod
    def get_absolute_gsutil_path(file_path, bucket_name):
        if file_path.startswith('gs://'):
            gsutil_absolute_path = file_path
        elif file_path.startswith(bucket_name):
            gsutil_absolute_path = os.path.join('gs://', file_path)
        else:
            gsutil_absolute_path = os.path.join('gs://', bucket_name, file_path)
        return gsutil_absolute_path

    @staticmethod
    def get_relative_path(file_path, bucket_name):
        if file_path.startswith('gs://'):
            relative_path = '/'.join(file_path.split('/')[3:])
        elif file_path.startswith(bucket_name):
            relative_path = '/'.join(file_path.split('/')[1:])
        else:
            relative_path = file_path
        return relative_path     

    @staticmethod
    def get_bucket_name(gcs_url):
        import re
        match = re.match(r"gs://([^/]+)/", gcs_url)
        bucket_name = match.group(1) if match else None
        return bucket_name