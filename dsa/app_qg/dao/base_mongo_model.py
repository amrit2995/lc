from configuration.mongo_connector import MongoConnector
from config.appConfigs import QGEN_MODEL_CONFIG
from helpers.common import UtilityClass


class BaseMongo:
    _init_connections = False 
    mongo_client = None
    envName = None
    nucleusHash = None

    def __init__(self,envName: str = 'stage', nucleusHash: str='',):
        BaseMongo.envName = envName
        BaseMongo.nucleusHash = nucleusHash
        BaseMongo.init_connections()
    
    @classmethod
    def init_connections(cls):
        if not cls._init_connections:
            BaseMongo.mongo_client = MongoConnector(
                env = BaseMongo.envName,
                clusterName = QGEN_MODEL_CONFIG["devClusterName"] if BaseMongo.envName == 'dev' else QGEN_MODEL_CONFIG["clusterName"],
                nucleusHash = BaseMongo.nucleusHash["db"]
            ).get_client()
            cls._init_connections = True
        else:
            UtilityClass.handleInfoLogs("BaseMongo Function has already been called.")
    
    def get_mongo_client(self):
        return BaseMongo.mongo_client
    
