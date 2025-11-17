
import math
from config.appConfigs import SCORE_CONFIG,COMMON_CONFIG
from service.base_service import BaseService
from helpers.nucleus import Nucleus
from helpers.common import UtilityClass


class QgenScorer(BaseService):
    def __init__(self):
        super().__init__()
        self.category_thresholds = self.get_category_thresholds_config(super().get_env(),super().get_qgen_nucleus_hash())
       
    def get_category_thresholds_config(self, envName: str = 'stage', nucleusHash: str=''):
        response =  Nucleus.get(env=envName, applicationName=SCORE_CONFIG["NUCLEUS"]["applicationName"][envName], 
                                scope=SCORE_CONFIG["NUCLEUS"]["scopeName"], nucleusHash=nucleusHash)
        return response["data"]

    def calculate_score(self,product,searchTermObj):
        try:
            searchTermObj["rawCategoryScore"]  = searchTermObj["categoryScore"]
            normalizedQCScore = UtilityClass.normalize_value(searchTermObj["categoryScore"],SCORE_CONFIG["QC_NORMALIZER"]["qcMinValue"],
                                        SCORE_CONFIG["QC_NORMALIZER"]["qcMaxValue"],SCORE_CONFIG["QC_NORMALIZER"]["qcNormalizedMinValue"],
                                        SCORE_CONFIG["QC_NORMALIZER"]["qcNormalizedMaxValue"])
            
            categoryMultiple = math.pow(normalizedQCScore, SCORE_CONFIG["CATEGORY_SCORE_MULTIPLIER"])
            searchTermObj["categoryScore"] = normalizedQCScore
            semanticMultiple = math.pow(searchTermObj["semanticScore"], SCORE_CONFIG["SEMANTIC_SCORE_MULTIPLIER"])
            queryLength  = math.pow(self.calculate_category_score(product,searchTermObj["searchTerm"]), 
                                    SCORE_CONFIG["QUERY_LENGTH_MULTIPLIER"])
            
            searchTermObj["queryLengthScore"] = queryLength

            qgenScore = (categoryMultiple * semanticMultiple * queryLength) ** SCORE_CONFIG["QGEN_DIVIDER"]
            normalizedQgenScore = UtilityClass.normalize_value(qgenScore,SCORE_CONFIG["QGEN_NORMALIZER"]["qgenMinValue"],
                                        SCORE_CONFIG["QGEN_NORMALIZER"]["qgenMaxValue"],SCORE_CONFIG["QGEN_NORMALIZER"]["qgenNormalizedMinValue"],
                                        SCORE_CONFIG["QGEN_NORMALIZER"]["qgenNormalizedMaxValue"])
            searchTermObj["qgenScore"] = round(normalizedQgenScore,COMMON_CONFIG["QGEN_ROUND_VALUE"])
            searchTermObj["rawQgenScore"] = round(qgenScore,COMMON_CONFIG["QGEN_ROUND_VALUE"])
            return searchTermObj
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Calculating QGEN Score",e)
    
    
    def calculate_category_score(self,product, searchTerm):
        considered_threshold = UtilityClass.get_category_threshold_config(self.category_thresholds,product)
        word_count = UtilityClass.count_words(searchTerm)

        if word_count > considered_threshold:
            exp_value = math.exp(considered_threshold / word_count)
            normalized_value = 1 / (1 + math.exp(-exp_value))
            return normalized_value
        
        return 1
    
    
    def get_scores_for_product(self,product,productSearchTermData,category_threshold):

        searchTermScoreArr = []
        if productSearchTermData and UtilityClass.validate_array(productSearchTermData["scores"]):
            for searchTermObj in productSearchTermData["scores"]:
                searchTermScoreArr.append(self.calculate_score(product,searchTermObj,category_threshold))

        finalProduct = {}
        finalProduct["productId"] = productSearchTermData["productId"]
        finalProduct["searchTermsList"] = searchTermScoreArr

        return finalProduct



        
            
        
