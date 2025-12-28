MONGO = {
    "applicationName" : {
        "dev": "spa-etl-dev",
        "stage": "spa-etl-stage",
        "prod": "spa-etl"
    },
    "scope" : {
        "onprem" :"mongo-onprem-connector",
        "delta" :"mongo-delta-connector",
        "southdeep" :"mongo-connector",
    },
}

ES = {
    "applicationName":{
        "stage": "spa-etl-stage",
        "prod": "spa-etl"
    },
    "scope":{
        "stage": "es-connector",
        "prod": "es-connector"
    },
}

POSTGRES = {
    "applicationName":{
        "dev": "spa-etl-dev",
        "stage": "spa-etl-stage",
        "prod": "spa-etl",
    },
    "scope":{
        "onprem": "postgres-credentials",
        "horizon": "postgres-horizon-connector",
        "revenue": "postgres-ent-connector"
    }
}

REDIS = {
    "applicationName" : {
        "stage":"spa-etl-stage",
        "prod":"spa-etl",
        "dev":"spa-etl-dev"
    },
    "scope":{
        "prod-east":"redis-prod-east-credentials",
        "prod-central":"redis-prod-central-credentials",
        "dev-east":"redis-dev-east-credentials",
        "stage-central":"redis-stage-central-credentials",
        "stage-east":"redis-stage-east-credentials"
    }
}

GCS = {
    "storage":
        {
            "applicationName" : {
                "dev": "spa-etl-dev",
                "stage": "spa-etl-stage",
                "prod": "spa-etl"
            },
            "scope" : {
                "dev" :"GCS-CREDENTIALS",
                "stage" :"GCS-CREDENTIALS",
                "prod" :"GCS-CREDENTIALS"
            },
            "bucketName" : {
                "dev" :"clwcirsmnp-medianetwork-dev",
                "stage" :"clwcirsmnp-medianetwork-stg",
                "prod" :"clwcirsmnp-medianetwork-prd"
            }
        },
    "bq":{
            "applicationName" : {
                "prod":"delta",
                "stage":"delta",
                "dev":"delta"
            },
            "scope":{
                "stage":"dataproc",
                "dev":"dataproc",
                "prod":"dataproc"
            }
        }
}

GCS_COMPOSER = {
    "storage": {
        "applicationName" : {
            "dev": "delta",
            "stage": "delta",
            "prod": "delta"
        },
        "scope" : {
            "dev" :"dataproc",
            "stage" :"dataproc",
            "prod" :"dataproc"
        },
        "bucketName" : {
            "stage":"us-east4-lormn-stage-compos-dbda358c-bucket",
            "dev":"us-east4-lormn-stage-compos-dbda358c-bucket",
            "prod":"us-central1-lormn-prod-comp-18ea420b-bucket"
        }
    }
}

GCP_PROJECT_MAPPING = {
    "stage": "gcp-ushi-mnp-stage",
    "prod": "gcp-ushi-mnp-prd",
    "dev": "gcp-ushi-mnp-dev"
}

GAM = {
    "applicationName" : {
        "dev": "GAM-SCRIPTS",
        "stage": "GAM-SCRIPTS",
        "prod": "GAM-SCRIPTS",
    },
    "scope" : {
        "dev": "GAM-CREDENTIALS",
        "stage": "GAM-CREDENTIALS",
        "prod": "GAM-CREDENTIALS"
    }
}

MINIO = {
    "applicationName" : {
        "dev": "spa-etl-dev",
        "stage": "spa-etl-stage",
        "prod": "spa-etl"
    },
    "scope" : {
        "dev" : "minio-credentials",
        "stage" : "minio-credentials",
        "prod" : "minio-credentials",
    },    
}
