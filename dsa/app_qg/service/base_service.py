import os
import json
from helpers.common import UtilityClass
from configuration.gcs_connector import GCSClient
from dao.qgen_model import QGenModel
from dao.clickstream_model import ClickStreamModel
from dao.qgen_batch_model import QGenBatchModel
from dao.category_model import CategoryModel
from dao.product_model import ProductModel
from config.configs import PROFILE, DEFAULT_PROFILE,SECRETS_CONFIG

class BaseService:
    _init_connections = False 
    gcs_client = None
    envName = DEFAULT_PROFILE
    nucleusHash = None


    def __init__(self):
        BaseService.envName = BaseService.get_env()
        BaseService.nucleusHash = BaseService.get_secrets()
        BaseService.init_connections()
        
        self.qgenModel = QGenModel(BaseService.envName,BaseService.nucleusHash)
        self.clickstreamModel = ClickStreamModel(BaseService.envName,BaseService.nucleusHash)
        self.categoryModel = CategoryModel(BaseService.envName,BaseService.nucleusHash)
        self.productModel = ProductModel(BaseService.envName,BaseService.nucleusHash)
        self.qgenBatchModel = QGenBatchModel(BaseService.envName,BaseService.nucleusHash)


    @classmethod
    def init_connections(cls):
        if not cls._init_connections:
            BaseService.gcs_client = GCSClient(
                env = BaseService.envName,
                nucleusHash = BaseService.nucleusHash["db"]
            )
            cls._init_connections = True
        else:
            UtilityClass.handleInfoLogs("Base Service init_connections has already been called.")


    
    def get_clickstream_model(self):
        return self.clickstreamModel


    def get_gcs_client(self):
        return BaseService.gcs_client
    
    def get_qgen_model(self):
        return self.qgenModel
    

    def get_qgen_batch_model(self):
        return self.qgenBatchModel
    
    def get_category_model(self):
        return self.categoryModel
    
    def get_product_model(self):
        return self.productModel
    

    @classmethod
    def get_env(cls):
        env_name = os.getenv(PROFILE, DEFAULT_PROFILE)
        return env_name
    

    @classmethod
    def get_secrets(cls):
        secrets_config = json.loads(os.getenv(SECRETS_CONFIG))
        if secrets_config["nucleusHash"] and secrets_config["nucleusHash"]:
            return secrets_config["nucleusHash"]
        return None


    
    def get_qgen_nucleus_hash(self):
        return BaseService.nucleusHash["qgen"]

