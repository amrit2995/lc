from dao.base_mongo_model import BaseMongo
from config.appConfigs import PRODUCT_FETCHER
from helpers.common import UtilityClass

class ProductModel(BaseMongo):
    def __init__(self, envName: str = 'stage', nucleusHash: str=''):
        super().__init__(envName,nucleusHash)
        self.db = super().get_mongo_client()[PRODUCT_FETCHER["devDatabase"]] if envName == 'dev' else super().get_mongo_client()[PRODUCT_FETCHER["database"]]
        self.collection = self.db[PRODUCT_FETCHER["collections"]["devProductMaster"]] if envName == 'dev' else self.db[PRODUCT_FETCHER["collections"]["productMaster"]]
    
    
    
    def find_by_id(self, productId):
        try:
            document = self.collection.find_one({"_id": productId})
            return document
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by ID: {e}")
            return None
        
    def find_by_ids(self, productIdArr):
        try:
            products = []
            documents = self.collection.find({"_id": {"$in" : productIdArr}})
            for document in documents:
                products.append(document)

            return products
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by ID: {e}")
            return None


