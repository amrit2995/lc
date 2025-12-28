
from martech_sdk.operators import BaseOperator
from martech_sdk.utils import logging
from google.cloud import storage
from martech_sdk.configs.env import EnvConfig
from io import BytesIO
import gzip
import os


class URIFormatTypes:
    GSUTIL = 'gsutil'
    PUBLIC = 'public'
    AUTHENTICATED = 'authenticated'

class StorageOperator(BaseOperator):

    storage_client: storage.Client = None
    bucket_name: str = EnvConfig.BUCKET.SOURCE

    def __init__(
            self,
            bucket_name: str=''
            ):
        super().__init__()
        self.bucket_name = bucket_name

    @classmethod
    def get_client(cls) -> storage.Client:
        if not cls.storage_client:
            logging.info('Creating Storage client.')
            cls.storage_client = storage.Client()
            logging.info('Storage client created.')
        logging.info(f'Returning Storage client.: {cls.storage_client}')
        logging.info(f'Project ID: {cls.storage_client.project}')
        return cls.storage_client
    
    @property
    def client(cls):
        return cls.get_client()

    def get_relative_path(self, file_path: str, bucket_name: str= ''):

        if not bucket_name:
            bucket_name = self.bucket_name

        logging.info("Getting relative path.")
        logging.info(f"File Path: {file_path}")
        logging.info(f"Bucket Name: {bucket_name}")
        if file_path.startswith('gs://'):
            relative_path = '/'.join(file_path.split('/')[3:])
        elif file_path.startswith(bucket_name):
            relative_path = '/'.join(file_path.split('/')[1:])
        else:
            relative_path = file_path
        logging.info(f"Final Relative Path: {relative_path}")
        return relative_path
    
    def get_bucket_name(self, gcs_url):
        import re
        match = re.match(r"gs://([^/]+)/", gcs_url)
        bucket_name = match.group(1) if match else None
        return bucket_name

    def get_absolute_path(self, file_path, bucket_name: str='', uri_type: str | URIFormatTypes= URIFormatTypes.GSUTIL):

        if not bucket_name:
            bucket_name = self.bucket_name

        logging.info("Getting absolute path.")
        logging.info(f"File Path: {file_path}")
        logging.info(f"Bucket Name: {bucket_name}")
        logging.info(f"URI Type: {uri_type}")
        if uri_type == URIFormatTypes.GSUTIL:
            if file_path.startswith('gs://'):
                gsutil_absolute_path = file_path
            elif file_path.startswith(bucket_name):
                gsutil_absolute_path = os.path.join('gs://', file_path)
            else:
                gsutil_absolute_path = os.path.join('gs://', bucket_name, file_path)
        logging.info(f"Final Absolute Path: {gsutil_absolute_path}")
        return gsutil_absolute_path

    def get_bucket_name_from_url(self, gcs_url):
        import re
        match = re.match(r"gs://([^/]+)/", gcs_url)
        bucket_name = match.group(1) if match else None
        return bucket_name
    
    def move_file_within_bucket(self, source, destination, bucket_name: str=''):

        try:
            source = self.get_relative_path(source)
            destination = self.get_relative_path(destination)
            if bucket_name:
                bucket = self.get_client().bucket(bucket_name)
            else:
                bucket = self.get_client().bucket(self.bucket_name)

            source_blob = bucket.blob(source)
            bucket.copy_blob(source_blob, bucket, destination)
            source_blob.delete()
            logging.info(f'Blob {source} renamed to {destination}.')
            return destination
        except Exception as e:
            logging.error(f"{type(e).__name__}:{e}")

    def download_file(self, source, destination, bucket_name=''):

        logging.info("Downloading file from GCS")
        if bucket_name:
            bucket = self.get_client().bucket(bucket_name)
        else:
            bucket = self.get_client().bucket(self.bucket_name)

        logging.info(f"Bucket: {bucket}")

        source = self.get_relative_path(source)
        blob = bucket.blob(source)
        blob.download_to_filename(destination)
        logging.info(f"File {source} downloaded to {destination}.")
        return destination

    def upload_file(
            self, 
            source, 
            destination, 
            bucket_name='', 
            content_type=None, 
            expiration=604800, 
            get_signed_url=False
            ):

        logging.info("Uploading file to GCS")

        if not bucket_name:
            bucket_name = self.bucket_name

        bucket = self.get_client().bucket(bucket_name)
        logging.info(f"Source: {source}")
        logging.info(f"Destination: {destination}")
        logging.info(f"Bucket: {bucket_name}")

        destination = self.get_relative_path(destination, bucket_name)
        blob = bucket.blob(destination)
        if not content_type:
            blob.upload_from_filename(source)
        else:
            blob.upload_from_filename(source, content_type=content_type)

        if get_signed_url:
            logging.info("Generating Signed URL")
            return self.get_signed_url(blob=blob, expiration=expiration)

        logging.info(f"File {source} uploaded to {destination}.")
        return True
        
    
    @classmethod
    def get_signed_url(cls,file_name='', blob=None, bucket_name='', expiration=604800): 

        if not blob:
            if not file_name:
                ValueError('Niether blob not file_name provided.')
            bucket = None
            if bucket_name:
                bucket = cls.get_client().bucket(bucket_name)
            else:
                bucket = cls.get_client().bucket(EnvConfig.BUCKET.SOURCE)

            file_name = cls.get_relative_path(file_name, bucket_name)
            blob = bucket.blob(file_name)
            
        logging.info("Generating Signed URL")
        logging.info(f"Bucket: {bucket}")
        logging.info(f"File Name: {file_name}")
        logging.info(f"Blob: {blob}")

        signed_url = blob.generate_signed_url(
            expiration=expiration,
            method='GET',
            version='v4'
        )
        return signed_url
    
    @classmethod
    def delete_file(cls, file_path, bucket_name=''):
        try:
            if bucket_name:
                bucket = cls.get_client().bucket(bucket_name)
            else:
                bucket = cls.get_client().bucket(EnvConfig.BUCKET.SOURCE)

            blob = bucket.get_blob(file_path)
            blob.delete()
            logging.info(f"Deleted the file: {file_path}")

        except Exception as e:
            logging.error(f"Faled: {e}")

    @classmethod
    def gzip_file(cls, source, destination, bucket_name='', get_signed_url=False):
        try:
            if bucket_name:
                bucket = cls.get_client().bucket(bucket_name)
            else:
                bucket = cls.get_client().bucket(EnvConfig.BUCKET.SOURCE)
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
                return cls.get_signed_url(blob=destination_blob)

            logging.info(f'File "{source}" compressed to "{destination}" in bucket "{bucket_name}".')

        except Exception as e:
            logging.error(f"Faled: {e}")