from delta_sdk.connectors.base import BaseConnector
from elasticsearch import Elasticsearch
import json
import ssl
from delta_sdk.utils import logging
from delta_sdk.configs.connConfigs import ES
from delta_sdk.utils.common import CommonUtils

class ESCreds:
    def __init__(self, host, username, code, root_file_path):
        self.host = host
        self.username = username
        self.code = code
        self.root_file_path = root_file_path

    def __call__(self, key=None):
        if hasattr(self, key):
            return getattr(self, key)
        return {'host': self.host, 'username': self.username, 'code':self.code, 'root_file_path': self.root_file_path}

    def __repr__(self):
        return f"ElasticSearchCreds(host={self.host}, username={self.username}, code={self.code}, root_file_path={self.root_file_path}"

class ESConnector(BaseConnector):
    def __init__(self,
                env: str = '',
                nucleusHash: str ='',
                base_path: str=''):
        super().__init__(env=env, applicationName=ES["applicationName"][env], scope=ES["scope"][env],
                          nucleusHash=nucleusHash, base_path=base_path)
        self._client: Elasticsearch = None

    def get_es_creds(self) -> ESCreds:
        data = self.get_creds()
        root_file_path = self._createCredsFile(data=json.dumps(data["root"]), file_name='esRoot.pem')

        host = data['host']
        username = data['username']
        code = data['password']

        es_creds = ESCreds(
            host=host,
            username=username,
            code=code,
            root_file_path=root_file_path
        )

        logging.info(es_creds)
        return es_creds

    @property
    @CommonUtils.retry_connection(max_retries=2, delay=1)
    def client(self) -> Elasticsearch:

        if not self._client:
            es_creds = self.get_es_creds()
            context = ssl.create_default_context(capath=es_creds.root_file_path)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            es =  Elasticsearch(
                es_creds.host,
                http_auth=(es_creds.username, es_creds.code),
                ssl_context=context,
                verify_certs=False,
                timeout=45
            )
            self._client = es

        logging.info(f"ES Client: {self._client}")
        return self._client