import asyncio
import json
from config.appConfigs import COMMON_CONFIG
from service.base_service import BaseService
from service.qgen_scorer import QgenScorer
from helpers.common import UtilityClass
from helpers.word_processor import WordProcessor


class KeywordService(BaseService):
    def __init__(self):
        super().__init__()
        self.qgenScorer = QgenScorer()
        UtilityClass.handleInfoLogs("KeywordService __init__ called")
        




    def set_searchTermObj(self,productObj):
        newProduct = {
            "productId" : productObj["_id"],
            "departmentDepth" : productObj["departmentDepth"] if "departmentDepth" in productObj and UtilityClass.validate_array(productObj["departmentDepth"]) else [],
            "description" : productObj["description"] if "description" in productObj and len(productObj["description"]) > 0 else "",
            "specs" : productObj["specs"] if "specs" in productObj and UtilityClass.validate_array(productObj["specs"]) else [],
            "bulletPoint" : json.loads(productObj["bulletPoint"]) if "bulletPoint" in productObj and len(productObj["bulletPoint"]) > 0 else [],
            "imageUrl":  productObj["imageUrl"] if "imageUrl" in productObj and len(productObj["imageUrl"]) > 0 else "",
            "ivm": productObj["ivm"] if "ivm" in productObj and len(productObj["ivm"]) > 0 else "",
            "brand": productObj["brand"] if "brand" in productObj and len(productObj["brand"]) > 0 else "",
            "vendorNumber": productObj["vendorNumber"] if "vendorNumber" in productObj and len(productObj["vendorNumber"]) > 0 else "",
            "version": productObj["version"] if "version" in productObj and len(productObj["version"]) > 0 else "",
            "modelId": productObj["modelId"] if "modelId" in productObj and len(productObj["modelId"]) > 0 else "",
            "itemNumber": productObj["itemNumber"] if "itemNumber" in productObj and len(productObj["itemNumber"]) > 0 else "",
            "pdURL" :  UtilityClass.create_pd_url(productObj["description"], productObj["_id"],productObj["brand"]) if "description" in productObj and len(productObj["description"]) > 0 else "",
            "searchTerms" : []
        }
        if 'searchTerms' in productObj:
            for searchTermObj in productObj['searchTerms']:
                newSearchTerm = {
                    "searchTerm":  searchTermObj["searchTerm"]if 'searchTerm' in searchTermObj else "",
                    # "searchTerm":  UtilityClass.clean_search_term(searchTermObj["searchTerm"]) if 'searchTerm' in searchTermObj else "",
                    "source": searchTermObj["source"] if 'source' in searchTermObj else "CLICKSTREAM",
                    "impressions": searchTermObj["impressions"] if 'impressions' in searchTermObj else 0,
                    "clicks": searchTermObj["clicks"] if 'clicks' in searchTermObj else 0,
                    "ctr": round(searchTermObj["ctr"],COMMON_CONFIG["CTR_ROUND_VALUE"]) if 'ctr' in searchTermObj else 0,
                    "semanticScore": round(searchTermObj["semanticScore"],COMMON_CONFIG["SEMANTIC_ROUND_VALUE"]) if 'semanticScore' in searchTermObj else COMMON_CONFIG["COSINE_SIMILARITY_BASELINE_SCORE"],
                    "categoryScore": searchTermObj["categoryScore"] if 'categoryScore' in searchTermObj else COMMON_CONFIG["CATEGORY_SCORE_BASELINE_SCORE"],
                    "qgenScore": round(searchTermObj["qgenScore"],COMMON_CONFIG["QGEN_ROUND_VALUE"]) if 'qgenScore' in searchTermObj else COMMON_CONFIG["QGEN_SCORE_BASELINE_SCORE"],
                }
                newProduct["searchTerms"].append(newSearchTerm)
        

        
        return newProduct

    def process_output(self,results):
        finalResult = {
            "QGEN" : {},
            "CLICKSTREAM" : {}
        }
        for result in results:
            if 'source' in result and result['source'] == 'QGEN' and 'products' in result and UtilityClass.validate_array(result['products']):
                for product in result['products']:
                    finalResult['QGEN'][product["_id"]] = self.set_searchTermObj(product)
            elif 'source' in result and result['source'] == 'CLICKSTREAM' and 'products' in result and UtilityClass.validate_array(result['products']):
                for product in result['products']:
                    finalResult['CLICKSTREAM'][product["_id"]] = self.set_searchTermObj(product)
                
        return finalResult



    
    def handle_clickstream_response(self,processedResult,omniItemId,output):
        if 'searchTerms' in processedResult['CLICKSTREAM'][omniItemId] and omniItemId in processedResult['QGEN'] and UtilityClass.validate_array(processedResult['CLICKSTREAM'][omniItemId]['searchTerms']):
            searchTermsProcessed = []
            for index, query in enumerate(processedResult['CLICKSTREAM'][omniItemId]['searchTerms']):
                query = self.qgenScorer.calculate_score(processedResult['QGEN'][omniItemId],query)
                if 'rawCategoryScore' in query:
                    del query['rawCategoryScore']
                if 'queryLengthScore' in query:
                    del query['queryLengthScore']
                if 'rawQgenScore' in query:
                    del query['rawQgenScore']
                searchTermsProcessed.append(query)
            
            if 'searchTerms' in output and UtilityClass.validate_array(output["searchTerms"]):
                output["searchTerms"].extend(searchTermsProcessed)
        
        return output



    async def get_keywords(self,input):
        try:
            tasks = [
                super().get_qgen_model().find_multiple_ids(input.omniItemIds)
            ]
            if input.increaseCoverage is True:
                tasks.append(super().get_clickstream_model().find_multiple_ids(input.omniItemIds))
            UtilityClass.handleInfoLogs("Parallel tasks",tasks)
            results = await asyncio.gather(*tasks)
            if results is not None and UtilityClass.validate_array(results):
                processedResult = self.process_output(results)
                output = {}
                for omniItemId in input.omniItemIds:
                    if omniItemId in processedResult['QGEN']:
                        output[omniItemId] = processedResult['QGEN'][omniItemId]

                    if omniItemId in processedResult['CLICKSTREAM'] and input.increaseCoverage is True:
                        output[omniItemId] = self.handle_clickstream_response(processedResult,omniItemId,output[omniItemId])

                    if 'searchTerms' in output[omniItemId] and UtilityClass.validate_array(output[omniItemId]['searchTerms']):
                        finalSearchTerms = []
                        for searchTermObj in output[omniItemId]['searchTerms']:
                            if not UtilityClass.element_exists(finalSearchTerms,'searchTerm',searchTermObj["searchTerm"]) and len(searchTermObj["searchTerm"]) < COMMON_CONFIG["SEARCH_TERM_CHARACTER_LIMIT"]:
                                finalSearchTerms.append(searchTermObj)

                        if input.increaseCoverage is True:
                            productResponse = super().get_product_model().find_by_id(omniItemId)
                            finalSearchTerms = super().get_category_model().get_category_valid_searchterms(productResponse,finalSearchTerms)
                        
                        finalSearchTerms = sorted(finalSearchTerms, key=lambda searchTerm: searchTerm['qgenScore'], reverse=True)
                        finalSearchTerms = [
                            item for item in finalSearchTerms
                            if input.qgenMinScore <= item['qgenScore'] <= input.qgenMaxScore
                        ]
                        output[omniItemId]['searchTerms'] = finalSearchTerms
                    
                
                if len(output) > 0:
                    return output
                
                return None
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Get Keywords Method",e)
            return None
        
    
    async def validate_keywords(self,input):
        try:
            spellCorrectedSearchTerms =[]
            products = super().get_product_model().find_by_ids(input.omniItemIds)
            if products is not None and UtilityClass.validate_array(products):
               if UtilityClass.validate_array(input.searchTerms):
                   for searchTerm in input.searchTerms:
                       searchTermObj = {
                           "originalSearchTerm" : searchTerm,
                           "searchTerm" :  WordProcessor.correct_and_singularize(searchTerm) if input.spellCheck else searchTerm
                       }
                       spellCorrectedSearchTerms.append(searchTermObj)
               categoryResponses = super().get_category_model().validate_searchterms(products,spellCorrectedSearchTerms)
               finalResponse = {}
               for product in products:
                   departmentDepth = []
                   if "Departments_Depth" in product:
                       departmentDepth = product["Departments_Depth"]
                   elif "departmentDepth" in product:
                       departmentDepth = product["departmentDepth"] 
                       
                   finalResponse[product["_id"]] = {
                       "productId" : product["_id"],
                       "description" : product["description"],
                       "brand" : product["brand"],
                       "departmentDepth" : departmentDepth,
                       "searchTerms" : categoryResponses[product["_id"]]
                   }
               return finalResponse

            return None
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Validate Keywords Method",e)
            return None
        
        


