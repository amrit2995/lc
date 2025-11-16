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
}

CLICKSTREAM_SEARCHTERM_FETCHER = {
    "clusterName" : "delta",
    "database": "qgen",
    "collections" : {
        "qgenCategory" : "clickstream_based_products_query"
    }
}

CATEGORY_FETCHER = {
    "clusterName" : "delta",
    "database": "qgen",
    "collection" : "searchterm_category_mapping"
}



PRODUCT_FETCHER = {
    "clusterName" : "delta",
    "database": "ingestion",
    "collections" : {
        "productMaster" : "products"
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
    "clusterName" : "delta",
    "database": "qgen",
    "collections" : {
        "rankedKeywords" : "qgen_master"
    },
    "projections" : {
        "_id":1,
        "searchTerms" :1,
        "departmentDepth" : 1

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