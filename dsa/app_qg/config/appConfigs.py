COMMON_CONFIG= {
    "COSINE_SIMILARITY_MIN_RANGE" : 1,
    "COSINE_SIMILARITY_MAX_RANGE" : 10,
    "CTR_ROUND_VALUE": 3,
    "QGEN_ROUND_VALUE": 2,
    "SEMANTIC_ROUND_VALUE" : 4,
    "COSINE_SIMILARITY_BASELINE_SCORE" : 8.4,
    "SEARCH_TERM_CHARACTER_LIMIT" : 100,
    "CATEGORY_SCORE_BASELINE_SCORE" : 1,
    "QGEN_SCORE_BASELINE_SCORE" : 1,
    "TIMEZONE_CONFIG": "US/Eastern",
    "LOG_FORMAT" : "airflow.task",
    "LOWES_PD_HOST_PREFIX" : "https://www.lowes.com/pd/"
}

CLICKSTREAM_SEARCHTERM_FETCHER = {
    "devClusterName" : "delta",
    "clusterName" : "onprem",
    "database": "qgen",
    "collections" : {
        "qgenCategory" : "clickstream_based_products_query"
    }
}

CATEGORY_FETCHER = {
    "devClusterName" : "delta",
    "clusterName" : "onprem",
    "database": "qgen",
    "collection" : "searchterm_category_mapping"
}



PRODUCT_FETCHER = {
    "devClusterName" : "delta",
    "clusterName" : "onprem",
    "database": "ml_lormn",
    "devDatabase": "ingestion",
    "collections" : {
        "productMaster" : "product_master_collection_delta",
        "devProductMaster" : "products"
    },
    "query": {"isPublished":"1" ,"isBuyable":"1","product_status_s": {"$ne":"DISPLAYONLY"},"brand" : {"$exists" : "true", "$ne" : ""},
              "description" : {"$exists" : "true", "$ne" : ""},"bulletPoint" : {"$exists" : "true", "$ne" : ""}},
    "fields" : {
        "_id" : 1,
        "productId" : 1,
        "brand" : 1,
        "description" : 1,
        "bulletPoint" : 1,
        "itemMasterLastModifiedDate" : 1,
        "itemNumber": 1,
        "modelId" : 1,
        "ivm":1,
        "added_date": 1,
        "departmentDepth" :1,
        "Departments_s" : 1
    },
    "BATCH_SIZE":50000
}

QGEN_MODEL_CONFIG = {
    "devClusterName" : "delta",
    "clusterName" : "onprem",
    "database": "qgen",
    "collections" : {
        "rankedKeywords" : "qgen_master"
    },
    "projections" : {
        "_id":1,
        "searchTerms" :1,
        "imageUrl": 1,
        "ivm": 1,
        "brand": 1,
        "vendorNumber": 1,
        "version": 1,
        "modelId": 1,
        "itemNumber": 1,
        "departmentDepth" : 1,
        "description": 1,
        "specs": 1,
        "bulletPoint": 1

    }
}

QGEN_BATCH_MODEL_CONFIG = {
    "devClusterName" : "delta",
    "clusterName" : "onprem",
    "database": "qgen",
    "collections" : {
        "keywords" : "file_download_requests"
    },
    "batchProcessingStatus" : {
        "processingState" : "PROCESSING",
        "completedState" : "COMPLETED",
        "errorState" : "ERROR"

    },
    "fileColumns" : {
        "keywordFile" : ["productId","description","brand","ivm","itemNumber","vendorNumber","modelId","departmentL1","departmentL2","departmentL3","departmentL4","departmentL5","departmentL6","searchTerm","impressions","clicks","ctr","qgenScore","semanticScore","categoryScore"]
    },
    "sortKey": {
        "uniqueSearchTermFile" : "impressions"
    },
    "fileNamePrefix" : {
        "qgenKeyWordFile" : "qgen-processed-file-"
    },
    "remotePath" : {
        "qgenKeyWordFile" : "Egress/vertex/qgen/"
    },
    "gcsLinkTTL" :{
         "qgenKeyWordFile" : 604800
    }
 }

SCORE_CONFIG = {
    "CATEGORY_SCORE_MULTIPLIER": 1,
    "SEMANTIC_SCORE_MULTIPLIER": 2,
    "QUERY_LENGTH_MULTIPLIER": 1,
    "QGEN_DIVIDER": 1,
    "QGEN_ROUND_UP_DECIMAL": 2,
    "NUCLEUS" : {
        "applicationName" : {
            "local": "qgen-dev",
            "dev": "qgen-dev",
            "stage": "qgen-stage",
            "prod": "qgen"
        },
        "scopeName" : "category-query-length"
    },
    "QC_NORMALIZER" : {
        "qcMinValue": 0,
        "qcMaxValue": 1,
        "qcNormalizedMinValue": 1,
        "qcNormalizedMaxValue": 10,
    },
    "QGEN_NORMALIZER" : {
        "qgenMinValue": 1,
        "qgenMaxValue": 1000,
        "qgenNormalizedMinValue": 1,
        "qgenNormalizedMaxValue": 10,
    }
}