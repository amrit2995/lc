from dao.base_mongo_model import BaseMongo
from config.appConfigs import CATEGORY_FETCHER
from helpers.common import UtilityClass
from helpers.searchTerm_processor import SearchTermProcessor

class CategoryModel(BaseMongo):
    def __init__(self, envName: str = 'stage', nucleusHash: str=''):
        super().__init__(envName,nucleusHash)
        self.db = super().get_mongo_client()[CATEGORY_FETCHER["database"]]
        self.collection = self.db[CATEGORY_FETCHER["collection"]] 
        
    
        
    def find_by_searchterm(self, searchTermArr):
        try:
            print("searchTermArr",searchTermArr)
            cursorDocuments = self.collection.find({"searchTerm": {"$in":searchTermArr}})
            if cursorDocuments:
                categoryResponses = []
                for document in cursorDocuments:
                    categoryResponses.append(document)
            return categoryResponses
        except Exception as e:
            UtilityClass.handleErrorLogs(f"Error finding document by ID: {e}")
            return None
    
    def get_category_valid_searchterms(self,productResponse,searchTerms):
        try:
            if productResponse and len(searchTerms) > 0:
                searchTermArr = []
                for searchTermObj in searchTerms:
                    searchTermArr.append(searchTermObj['searchTerm'])
                categoryResponses = self.find_by_searchterm(searchTermArr)
                if categoryResponses and UtilityClass.validate_array(categoryResponses):
                    return SearchTermProcessor.get_valid_searchterms(searchTerms,categoryResponses,productResponse)
                else:
                    return searchTerms

            else:
                return searchTerms
            
        except Exception as e:
            UtilityClass.handleErrorLogs("Error",e)
            return None
        
    def handleSearchtermNotFound(self,searchTermsArr):
        newSeachTermArr = []

        if searchTermsArr and len(searchTermsArr) > 0:
            for searchTerm in searchTermsArr:
                searchTermObj =  {
                    "searchTerm" : searchTerm['searchTerm'],
                    "originalSearchTerm" : searchTerm['originalSearchTerm'],
                    "valid": True
                }
                newSeachTermArr.append(searchTermObj)
        
        return newSeachTermArr

    def validate_searchterms(self,productResponses,searchTermsArr):
        try:
            finalResponse = {}
            searchTerms = []
            if len(searchTermsArr) > 0:
                for searchTermObj in searchTermsArr:
                    searchTerms.append(searchTermObj["originalSearchTerm"])
                    searchTerms.append(searchTermObj["searchTerm"])

                categoryResponses = self.find_by_searchterm(searchTerms)
                if categoryResponses and UtilityClass.validate_array(categoryResponses):
                    for productResponse in productResponses:
                        finalResponse[productResponse["_id"]] = SearchTermProcessor.get_valid_invalid_searchtermList(searchTermsArr,categoryResponses,productResponse)
                else:
                    for productResponse in productResponses:
                        finalResponse[productResponse["_id"]] = self.handleSearchtermNotFound(searchTermsArr)
            else:
                for productResponse in productResponses:
                    finalResponse[productResponse["_id"]] = self.handleSearchtermNotFound(searchTermsArr)

            return finalResponse
            
        except Exception as e:
            UtilityClass.handleErrorLogs("Error",e)
            return None
    
    
