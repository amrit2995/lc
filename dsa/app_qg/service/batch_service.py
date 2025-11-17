import uuid
from filelock import FileLock
from config.appConfigs import QGEN_BATCH_MODEL_CONFIG
from helpers.common import UtilityClass
from helpers.searchTerm_file_processor import SearchTermFileProcessor
from service.keyword_service import KeywordService


class BatchService(KeywordService):
    LOCK_FILE_PATH = UtilityClass._createTempFile("tasks.lock")
    async def get_keywords_file(self,input,requestId):
        try:
            lock = FileLock(BatchService.LOCK_FILE_PATH)
            with lock:
                UtilityClass.handleInfoLogs("calling get_keywords_file",input)
                results = await super().get_keywords(input)
                
                gcsFileLink = None
                gcsFilePath = None
                bucketName = super(KeywordService,self).get_gcs_client().get_bucket_name()
                searchTerms = SearchTermFileProcessor.parseSearchTerms(results,super().get_product_model())
                UtilityClass.handleInfoLogs("Search Terms fetched successfully",len(searchTerms))
                if searchTerms:
                    searchTermFilePath = SearchTermFileProcessor.createSearchTermFile(searchTerms)
                    if searchTermFilePath:
                        gcsFilePath,gcsFileLink = SearchTermFileProcessor.createSearchTermFileLink(searchTermFilePath,super(KeywordService,self).get_gcs_client())
                gcsPrefixPath =  "gs://" + bucketName + "/"
                outputObj = {
                    "requestData" : input.dict(),
                    "requestTimeStamp" : UtilityClass.getCurrentTS(),
                    "output" : {
                        "gcsFilePath" : gcsPrefixPath +  gcsFilePath if gcsFilePath else "",
                        "gcsFileLink" : gcsFileLink if gcsFileLink else ""
                    },
                    "status" : QGEN_BATCH_MODEL_CONFIG["batchProcessingStatus"]["completedState"]  if gcsFilePath else QGEN_BATCH_MODEL_CONFIG["batchProcessingStatus"]["errorState"]
                }
                UtilityClass.handleInfoLogs("outputObj",outputObj)
                upsertResult = super(KeywordService,self).get_qgen_batch_model().upsert_by_id(requestId,(outputObj))   

                UtilityClass.handleInfoLogs("upsertResult",upsertResult)
                if input.webhookUrl:
                    UtilityClass.post_object_to_url_with_retry(input.webhookUrl,outputObj)
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Get Keywords File Method",e)
            return None
    
    def call_keywords_file(self,input,requestId,background_tasks):
        background_tasks.add_task(self.get_keywords_file, input,requestId)
        return "Keyword Method Called"
    
    async def submit_batch_products(self,input, background_tasks):
        try:
            requestId = str(uuid.uuid4())
            self.call_keywords_file(input,requestId,background_tasks)
            requestObj = {
                "requestId" : requestId,
                "requestData" : input.dict(),
                "requestTimeStamp" : UtilityClass.getCurrentTS(),
                "status" : QGEN_BATCH_MODEL_CONFIG["batchProcessingStatus"]["processingState"]
            }
            upsertResult = super(KeywordService,self).get_qgen_batch_model().upsert_by_id(requestId,(requestObj))   
            UtilityClass.handleInfoLogs("upsertResult",upsertResult)
            requestObj["requestId"] = requestId
            return requestObj
        
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Get Keywords File Method",e)
            return None
    
    async def fetch_by_request_id(self,requestId):
        try:
            fetchResult = super(KeywordService,self).get_qgen_batch_model().find_by_id(requestId)   
            del fetchResult["_id"]
            if fetchResult:
                return fetchResult
            return None
        
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Fetch by Request Id",e)
            return None