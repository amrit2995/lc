import pandas as pd
from datetime import datetime
from helpers.common import UtilityClass
from config.appConfigs import QGEN_BATCH_MODEL_CONFIG

class SearchTermFileProcessor:


    @staticmethod
    def parseSearchTerms(results,product_model):
        try:
            searchTerms = []
            for key in results:
                productResponse = product_model.find_by_id(key)
                departmentL1 = ""
                departmentL2 = ""
                departmentL3 = ""
                departmentL4 = ""
                departmentL5 = ""
                departmentL6 = ""
                departments = []
                if "Departments_s" in productResponse and len(productResponse["Departments_s"]) > 0:
                    departments = productResponse["Departments_s"].strip('/').split('/')
                    departmentL1 = departments[0] if len(departments) > 0 else ""
                    departmentL2 = departments[1] if len(departments) > 1 else ""
                    departmentL3 = departments[2] if len(departments) > 2 else ""
                    departmentL4 = departments[3] if len(departments) > 3 else ""
                    departmentL5 = departments[4] if len(departments) > 4 else ""
                    departmentL6 = departments[5] if len(departments) > 5 else ""

                if 'searchTerms' in results[key] and UtilityClass.validate_array(results[key]['searchTerms']):
                    for searchTermObj in results[key]['searchTerms']:
                        searchTermObj['productId'] =  key
                        searchTermObj['description'] =  productResponse['description']  if 'description' in productResponse else ""
                        searchTermObj['brand'] =  productResponse['brand'] if 'brand' in productResponse else ""
                        searchTermObj['departmentL1'] = departmentL1
                        searchTermObj['departmentL2'] = departmentL2
                        searchTermObj['departmentL3'] = departmentL3
                        searchTermObj['departmentL4'] = departmentL4
                        searchTermObj['departmentL5'] = departmentL5
                        searchTermObj['departmentL6'] = departmentL6
                        searchTermObj['itemNumber'] =  productResponse['itemNumber'] if 'itemNumber' in productResponse else ""
                        searchTermObj['ivm'] =  productResponse['ivm'] if 'ivm' in productResponse else ""
                        searchTermObj['vendorNumber'] =  productResponse['vendorNumber'] if 'vendorNumber' in productResponse else ""
                        searchTermObj['modelId'] =  productResponse['modelId']  if 'modelId' in productResponse else ""
                        del searchTermObj['source']
                        searchTerms.append(searchTermObj)
            
            if UtilityClass.validate_array(searchTerms):
                return searchTerms
            return None
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Parsing Search Terms",e)
            return None



    @staticmethod
    def createSearchTermFile(results):
        try:
            if UtilityClass.validate_array(results):
                productDf = pd.DataFrame(results)
                productDf = productDf[QGEN_BATCH_MODEL_CONFIG['fileColumns']['keywordFile']] 

                finalSearchTerms = {}
                for result in results:
                    if 'searchTerm' in result:
                        if result['searchTerm'] in finalSearchTerms:
                            finalSearchTerms[result['searchTerm']]['impressions'] += result['impressions']
                            finalSearchTerms[result['searchTerm']]['clicks'] += result['clicks']
                        else:
                            finalSearchTerms[result['searchTerm']] = {}
                            finalSearchTerms[result['searchTerm']]['impressions'] = result['impressions']
                            finalSearchTerms[result['searchTerm']]['clicks'] = result['clicks']
                        
                        
                transformed = [{"searchTerm": key, **value} for key, value in finalSearchTerms.items()]
                sortedSearchTerms = UtilityClass.sort_objects(transformed,QGEN_BATCH_MODEL_CONFIG['sortKey']['uniqueSearchTermFile'], reverse=True)
                uniqueSearchTermDf = pd.DataFrame(sortedSearchTerms)
                
                outputFilePath = UtilityClass._createTempFile(QGEN_BATCH_MODEL_CONFIG['fileNamePrefix']['qgenKeyWordFile'] +  datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".xlsx")
                with pd.ExcelWriter(outputFilePath, engine="xlsxwriter") as writer:
                    productDf.to_excel(writer, sheet_name="ProductId Based Search Terms", index=False)
                    uniqueSearchTermDf.to_excel(writer, sheet_name="Unique Search Terms", index=False)

                return outputFilePath
            
            return None
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Creating Search Term File",e)
            return None
    
    @staticmethod
    def createSearchTermFileLink(filePath,gcs_client):
        try:
            destinationFileName = QGEN_BATCH_MODEL_CONFIG['remotePath']['qgenKeyWordFile'] + filePath.rsplit('/', 1)[-1]
            if gcs_client:
                remotePath = gcs_client.upload_file(filePath, destinationFileName)
                if remotePath:
                    gcsFileLink = gcs_client.create_v4_presigned_url(remotePath,QGEN_BATCH_MODEL_CONFIG['gcsLinkTTL']['qgenKeyWordFile'])
                    UtilityClass.delete_file(filePath)
                    return remotePath,gcsFileLink
            return None,None
        except Exception as e:
            UtilityClass.handleErrorLogs("Error in Creating Search Term File Link",e)
            return None,None
        
            




        





