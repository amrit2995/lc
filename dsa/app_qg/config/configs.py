NUCLEUS={
    "host": {
        "local": "https://internal-east4.carbon-stage.gcp.lowes.com",
        "dev": "https://internal-east4.carbon-stage.gcp.lowes.com",
        "stage": "https://internal-east4.carbon-stage.gcp.lowes.com",
        "prod": "https://internal-east4.carbon.gcp.lowes.com",
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
            "local": "spa-etl-dev",
            "dev": "spa-etl-dev",
            "stage": "spa-etl-stage",
            "prod": "spa-etl"
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
        "local": "spa-etl-dev",
        "dev": "spa-etl-dev",
        "stage": "spa-etl-stage",
        "prod": "spa-etl"
    },
     "scope" : {
        "local" :"GCS-CREDENTIALS",
        "dev" :"GCS-CREDENTIALS",
        "stage" :"GCS-CREDENTIALS",
        "prod" :"GCS-CREDENTIALS"
    },
    "bucketName" : {
        "local" :"clwcirsmnp-medianetwork-dev",
        "dev" :"clwcirsmnp-medianetwork-dev",
        "stage" :"clwcirsmnp-medianetwork-stg",
        "prod" :"clwcirsmnp-medianetwork-prd"
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
DEFAULT_PROFILE = 'prod'
STRING_EMPTY = ""
GOOGLE_APPLICATION_CREDENTIALS = '/Users/3560586/Documents/code/lowes/recommendations/sponsored-products/secrets/secrets'
SERVER_NOT_READY = 'Server is not ready'
SERVER_READY = 'Server is Ready.'
SERVER_LIVE = 'Server is Live.'
SERVICE_UNAVAILABLE = 'Service Unavailable.'