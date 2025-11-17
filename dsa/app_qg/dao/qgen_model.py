from dao.base_mongo_model import BaseMongo
from config.appConfigs import QGEN_MODEL_CONFIG
from helpers.common import UtilityClass


class QGenModel(BaseMongo):
    def __init__(self, envName: str = 'stage', nucleusHash: str=''):
        super().__init__(envName,nucleusHash)
        self.db = super().get_mongo_client()[QGEN_MODEL_CONFIG["database"]]
        self.collection = self.db[QGEN_MODEL_CONFIG["collections"]["rankedKeywords"]]
        
    
    def find_by_id(self, productId):
        try:
            document = self.collection.find_one({"_id": productId})
            return document
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by ID: {e}")
            return None
    
    async def find_multiple_ids(self, productIdArr):
        finalDocuments = {
            "source": "QGEN",
            "products": None
        }
        try:
            documents = self.collection.find({"_id": {"$in":productIdArr}},projection=QGEN_MODEL_CONFIG["projections"])
            finalDocuments["products"] = [] 
            for document in documents:
                finalDocuments["products"].append(document)
            return finalDocuments
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by ID: {e}")
            return finalDocuments
    