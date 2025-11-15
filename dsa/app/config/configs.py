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

NUCLEUS={
    "host": {
        "local": "<local>",
        "dev": "<dev>",
        "stage": "<stage>",
        "prod": "<prod>",
    },
    "uri" : {
        "getConfig" : "/nucleus/config?scope={scopeName}&applicationName={applicationName}",
        "viewConfig" : "/nucleus/config/view?scope={scopeName}&applicationName={applicationName}",
        "saveConfig" : "/nucleus/config",
        "updateConfig" : "/nucleus/config/update"
    }
}
DB={
    "mongo" : {
        "applicationName" : {
            "local": "<local>",
            "dev": "<dev>",
            "stage": "<stage>",
            "prod": "<prod>"
        },
        "scope" : {
            "onprem" :"mongo-onprem-connector",
            "delta" :"mongo-delta-connector",
            "southdeep" :"mongo-connector",
        },
        "maxRetries": 5,
        "delay" : 10
    
    },
    "mongoLocal" : {
        "uri": "mongodb://localhost:27017/"
    }
}

GCS={
    "applicationName" : {
        "local": "<local>",
        "dev": "<dev>",
        "stage": "<stage>",
        "prod": "<prod>"
    },
     "scope" : {
        "local" :"GCS-CREDENTIALS",
        "dev" :"GCS-CREDENTIALS",
        "stage" :"GCS-CREDENTIALS",
        "prod" :"GCS-CREDENTIALS"
    },
    "bucketName" : {
        "local" :"<local>",
        "dev" :"<dev>",
        "stage" :"<stage>",
        "prod" :"<prod>"
    }
}

REQUEST_CONFIG ={
    "maxRetries": 3,
    "delay" : 2
}
CONFIG_FILE_PATH = 'resources/application.yaml'
PROFILE = 'profile'
SECRETS_CONFIG = "SECRETS_CONFIG"
DB_NUCLEUS_HASH = "db_hash"
QGEN_NUCLEUS_HASH = "qgen_hash"
DEFAULT_PROFILE = 'dev'
STRING_EMPTY = ""
GOOGLE_APPLICATION_CREDENTIALS = '<local>'
SERVER_NOT_READY = 'Server is not ready'
SERVER_READY = 'Server is Ready.'
SERVER_LIVE = 'Server is Live.'
SERVICE_UNAVAILABLE = 'Service Unavailable.'