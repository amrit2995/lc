from dao.base_mongo_model import BaseMongo
from config.appConfigs import QGEN_BATCH_MODEL_CONFIG
from helpers.common import UtilityClass


class QGenBatchModel(BaseMongo):
    def __init__(self, envName: str = 'stage', nucleusHash: str=''):
        super().__init__(envName,nucleusHash)
        self.db = super().get_mongo_client()[QGEN_BATCH_MODEL_CONFIG["database"]]
        self.collection = self.db[QGEN_BATCH_MODEL_CONFIG["collections"]["keywords"]]
        
    
    def find_by_id(self, requestId):
        try:
            document = self.collection.find_one({"_id": requestId})
            return document
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by Request ID: {e}")
            return None
    
    def upsert_by_id(self, requestId, update_data):
        try:
            result = self.collection.update_one({"_id": requestId}, {"$set": update_data}, upsert=True)
            if result.upserted_id:
                UtilityClass.handleInfoLogs(f"Document inserted with Request ID: {result.upserted_id}")
            else:
                UtilityClass.handleInfoLogs(f"Document updated with Request ID: {requestId}")
            return result
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error upserting document: {e}")
            return None