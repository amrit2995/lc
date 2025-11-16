from helpers.common import UtilityClass
class SearchTermProcessor:

    @staticmethod
    def update_category_set(category,categorySet):
        categoryParts = category.split('$$')
        categorySet.update(categoryParts)
        return categorySet

    @staticmethod
    def get_search_term_categories(categoryResponse): 
        categorySet = set()
        if "qusResponse" in categoryResponse and "qcResponse" in categoryResponse["qusResponse"]:
            if "qcFilter" in categoryResponse["qusResponse"]["qcResponse"] and len(categoryResponse["qusResponse"]["qcResponse"]["qcFilter"]) > 0:
                categorySet = SearchTermProcessor.update_category_set(categoryResponse["qusResponse"]["qcResponse"]["qcFilter"],categorySet)
            
            if "categoryFilter" in categoryResponse["qusResponse"]["qcResponse"] and len(categoryResponse["qusResponse"]["qcResponse"]["categoryFilter"]) > 0:
                categorySet = SearchTermProcessor.update_category_set(categoryResponse["qusResponse"]["qcResponse"]["categoryFilter"],categorySet)

            if "predictions" in categoryResponse["qusResponse"]["qcResponse"] and UtilityClass.validate_array(categoryResponse["qusResponse"]["qcResponse"]["predictions"]):
                for prediction in categoryResponse["qusResponse"]["qcResponse"]["predictions"]:
                    if "departmentLevel4" in prediction and len(prediction["departmentLevel4"].strip()) > 0:
                        categorySet = SearchTermProcessor.update_category_set(prediction["departmentLevel4"],categorySet)
                    elif "departmentLevel3" in prediction and len(prediction["departmentLevel3"].strip()) > 0:
                        categorySet = SearchTermProcessor.update_category_set(prediction["departmentLevel3"],categorySet)
                    elif "departmentLevel2" in prediction and len(prediction["departmentLevel2"].strip()) > 0:
                        categorySet = SearchTermProcessor.update_category_set(prediction["departmentLevel2"],categorySet)
            
            if "nerDeptPredictions" in categoryResponse["qusResponse"]["qcResponse"] and UtilityClass.validate_array(categoryResponse["qusResponse"]["qcResponse"]["nerDeptPredictions"]):
                for depthPrediction in categoryResponse["qusResponse"]["qcResponse"]["nerDeptPredictions"]:
                    if "specValue" in depthPrediction:
                        categorySet = SearchTermProcessor.update_category_set(depthPrediction["specValue"],categorySet)
        categorySet = {s for s in categorySet if s}
        return categorySet
    
    @staticmethod
    def findLargestCategoryMatch(categorySet,productDepartmentArr):
        categorySetLargest = UtilityClass.get_largest_by_starting_integer(categorySet)
        if UtilityClass.validate_array(productDepartmentArr):
            if (categorySetLargest[0].count("/") - 1) == productDepartmentArr[0].count("/"):
                for category in categorySetLargest:
                    if productDepartmentArr[0] in category:
                        return True
                
                return False
            else:
                return True   
        
        else:
            return True 



    @staticmethod
    def category_match(categoryResponse,productDepartment):
        productDepartment = productDepartment.lstrip("/")
        productDepartmentArr = UtilityClass.remove_last_slash_recursively(productDepartment) 
        productDepartmentArr = productDepartmentArr[:-1]
        categorySet = SearchTermProcessor.get_search_term_categories(categoryResponse)
        if len(categorySet) == 0:
            return True
        
        largestCategoryMatch = SearchTermProcessor.findLargestCategoryMatch(categorySet,productDepartmentArr)
        if largestCategoryMatch:
            for productDepartment in  productDepartmentArr:
                for category in categorySet:
                    if productDepartment in category:
                        return True
            return False
        else:
            return False

    @staticmethod
    def spec_match(categoryResponse,product):
        combined_ner = []

        if "qcResponse" in categoryResponse["qusResponse"] and  "ner" in categoryResponse["qusResponse"]["qcResponse"]:
            combined_ner.extend(categoryResponse["qusResponse"]["qcResponse"]["ner"])
        

        specs = {}
        for spec in combined_ner:
            if "brand" in spec["specLabel"].lower():
                spec["specLabel"] = "brand"
            if spec["specLabel"] != 'Departments_Depth' and spec["specLabel"] != 'departmentDepth' :
                specs.setdefault(spec["specLabel"], []).append(spec["specValue"].lower())
        
        for key, arr in specs.items():
            if key in product:
                val = product.get(key, '').lower()
                for element in arr:
                    if element.lower() not in val.lower():
                        return False
                        
        
        return True
    

    @staticmethod
    def is_valid_searchterm(categoryResponse,product):
        if  "queryType" not in categoryResponse["qusResponse"] or categoryResponse["qusResponse"]["queryType"] == "TAIL":
            return True
        if product and "Departments_s" in product and len(product["Departments_s"]) > 0 and categoryResponse and categoryResponse["categoryResponseReceived"].lower() == "true":
            isCategoryMatch = SearchTermProcessor.category_match(categoryResponse,product["Departments_s"])
            isSpecMatch = SearchTermProcessor.spec_match(categoryResponse,product)
            
            if not isCategoryMatch or not isSpecMatch:
                return False

        return True

    @staticmethod
    def get_valid_searchterms(searchTerms,categoryDbResponse,product):
        try:
            if categoryDbResponse and UtilityClass.validate_array(categoryDbResponse):
                searchTermCategories = {}
                newSearchTermArr = []
                for category in categoryDbResponse:
                    key = category['searchTerm']
                    searchTermCategories[key] = category
                if searchTerms and UtilityClass.validate_array(searchTerms):
                    for searchTermObj in searchTerms:
                        if searchTermObj["searchTerm"] in searchTermCategories:
                            if SearchTermProcessor.is_valid_searchterm(searchTermCategories[searchTermObj["searchTerm"]],product):
                                UtilityClass.handleInfoLogs(f"Valid Search Term :{searchTermObj['searchTerm']} for Product : {product['_id']}")
                                newSearchTermArr.append(searchTermObj)
                            else:
                                UtilityClass.handleInfoLogs(f"Invalid Search Term :{searchTermObj['searchTerm']} for Product : {product['_id']}")
                                
                        else:
                            newSearchTermArr.append(searchTermObj)

            return newSearchTermArr
        except Exception as e:
            UtilityClass.handleErrorLogs("Error",e)


    @staticmethod
    def get_valid_invalid_searchtermList(searchTermsArr,categoryDbResponse,product):
        try:
            if categoryDbResponse and UtilityClass.validate_array(categoryDbResponse):
                searchTermCategories = {}
                newSearchTermArr = []
                for category in categoryDbResponse:
                    key = category['searchTerm']
                    searchTermCategories[key] = category
                if searchTermsArr and UtilityClass.validate_array(searchTermsArr):
                    for searchTermObj in searchTermsArr:
                        if 'searchTerm' in searchTermObj and searchTermObj['searchTerm'] in searchTermCategories:
                            if SearchTermProcessor.is_valid_searchterm(searchTermCategories[searchTermObj['searchTerm']],product):
                                searchTermObj["valid"] = True
                            else:
                                searchTermObj["valid"] = False
                        elif 'originalSearchTerm' in searchTermObj and searchTermObj['originalSearchTerm'] in searchTermCategories:
                            if SearchTermProcessor.is_valid_searchterm(searchTermCategories[searchTermObj['originalSearchTerm']],product):
                                searchTermObj["valid"] = True
                            else:
                                searchTermObj["valid"] = False
                        else:
                            searchTermObj["valid"] = True
                        newSearchTermArr.append(searchTermObj)

            return newSearchTermArr
        except Exception as e:
            UtilityClass.handleErrorLogs("Error",e)




        


        
            


                

            
                    




