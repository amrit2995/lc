from dao.base_mongo_model import BaseMongo
from config.appConfigs import CLICKSTREAM_SEARCHTERM_FETCHER
from helpers.common import UtilityClass

class ClickStreamModel(BaseMongo):
    def __init__(self, envName: str = 'stage', nucleusHash: str=''):
        super().__init__(envName,nucleusHash)
        self.db = super().get_mongo_client()[CLICKSTREAM_SEARCHTERM_FETCHER["database"]]
        self.collection = self.db[CLICKSTREAM_SEARCHTERM_FETCHER["collections"]["qgenCategory"]]

        
    
    def find_by_id(self, productId):
        try:
            document = self.collection.find_one({"_id": productId})
            return document
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by ID: {e}")
            return None
    
    async def find_multiple_ids(self, productIdArr):
        finalDocuments = {
            "source": "CLICKSTREAM",
            "products": None
        }
        try:
            documents = self.collection.find({"_id": {"$in":productIdArr}})
            finalDocuments["products"] = [] 
            for document in documents:
                finalDocuments["products"].append(document)
            return finalDocuments
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by ID: {e}")
            return finalDocuments
    