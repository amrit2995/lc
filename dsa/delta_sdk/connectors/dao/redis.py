from delta_sdk.configs.connConfigs import REDIS

from delta_sdk.connectors.base import BaseConnector
from delta_sdk.utils.common import CommonUtils
from redis import Redis

class RedisConnector(BaseConnector):
    def __init__(self, 
                env: str = '',
                clusterName: str ='', 
                nucleusHash: str ='',
                isTLS: bool=True,
                base_path: str='',
                region: str='east'):
        super().__init__(env=env, applicationName=REDIS["redis"]["applicationName"][env], scope=REDIS["redis"]["scope"][clusterName],
                          nucleusHash=nucleusHash, base_path=base_path, region=region)
        self.isTLS = isTLS
        self._client = None

    def get_redis_creds(self):
        # return 
        data = self.get_creds()

        client_cert = ''
        client_key = ''

        if data.get('client_cert', None):
            client_cert = self._createCredsFile(data=data['client_cert'], file_name='client_cert.pem')

        if data.get('client_key', None):
            client_key = self._createCredsFile(data=data['client_key'], file_name='client_key.pem')


        host = data.get('host')
        code = data.get('password')
        port = data.get('port')
        username = data.get('username')

        return (host, port, username, code)

    @property
    @CommonUtils.retry_connection(max_retries=1, delay=1)
    def client(self):

        if not self._client:
            host, port, username, code = self.get_redis_creds()
            self._client = Redis(
                    host=host,
                    port=port,
                    username=username,
                    password=code,
                    ssl=True
            )
        # logging.info("Ping successful",r.ping())
        return self._client

