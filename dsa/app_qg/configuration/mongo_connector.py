import pymongo
from configuration.base_connector import BaseConnector
from helpers.common import UtilityClass
from config.configs import DB

class MongoConnector(BaseConnector):
    def __init__(self, 
                env: str = '',
                clusterName: str ='', 
                nucleusHash: str ='',
                isTLS: bool=True,
                base_path: str=''):
        super().__init__(env=env, applicationName=DB["mongo"]["applicationName"][env], scope=DB["mongo"]["scope"][clusterName],
                          nucleusHash=nucleusHash, base_path=base_path)
        self.isTLS = isTLS
        self.client = None
        self.client = self.get_client()

    def get_mongo_creds(self):
        # return 
        data = self.get_creds()

        cert_path = self._createCredsFile(data=data['ca'], file_name='caFile.pem')
        key_path = self._createCredsFile(data=data['key'], file_name='keyFile.pem')
        host = data['host']

        return [host, cert_path, key_path]


    @BaseConnector.retry_connection(max_retries=5, delay=10)
    def get_client(self):
        if self.client is None:
            if self.isTLS:
                self.client = self.connectMongoTLS()
            else:
                self.client = self.connectMongoNoTLS()

        return self.client

    def connectMongoNoTLS(self):
        mongoClient = pymongo.MongoClient(DB['mongo']['mongoLocal']['uri'])
        UtilityClass.handleInfoLogs("Mongo server details local:")
        return mongoClient

    def connectMongoTLS(self):
        host, cert_path, key_path = self.get_mongo_creds()
        UtilityClass.handleInfoLogs("host",host)
        UtilityClass.handleInfoLogs("cert_path",cert_path)
        UtilityClass.handleInfoLogs("key_path",key_path)
        mongoClient = pymongo.MongoClient(host,
            tls=self.isTLS,
            tlsCAFile=cert_path
            )
        UtilityClass.handleInfoLogs("Mongo server details remote:",mongoClient.server_info())
        return mongoClient