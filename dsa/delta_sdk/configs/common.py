import warnings
class InfraType:
    DATAPROC='dataproc'
    ON_PREM='onprem'
    COMPOSER='composer'

REQUEST_CONFIG ={
    "maxRetries": 3,
    "delay" : 2
}

warnings.warn(
    "COMMON_CONFIG will soon be Depricated, Use CommonConfig class instead. ",
    DeprecationWarning,
    stacklevel=2
)
COMMON_CONFIG= {
    "TIMEZONE_CONFIG": "US/Eastern",
    "LOG_FORMAT" : "airflow.task",
    "DEFAULT_LOG_FORMAT": "%(asctime)s - %(name)s %(levelname)s - %(message)s",
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M:%S"
}

class CommonConfig:
    TIMEZONE_CONFIG = "US/Eastern"
    AIRFLOW_LOG_FORMAT = "airflow.task"
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    GIT_HTTP_MNP_REPO_URL = "https://tools.lowes.com/stash/scm/e-mnp/<REPO-NAME>.git"
    GIT_HTTP_TOKEN_HEADER = f"http.extraHeader=\"Authorization: Bearer <TOKEN>\""

CERTS = {
    "gcs_bucket": {
        "mongo":{
                "delta": {
                    "dev":{
                        "trustStorePath": "gs://clwcirsmnp-medianetwork-dev/dataproc-essentials/mongo/dev/mongo-delta-ca",
                        "keyStorePath": "gs://clwcirsmnp-medianetwork-dev/dataproc-essentials/mongo/dev/mongo-delta.pkcs12",
                        "sparkProperties": "gs://clwcirsmnp-medianetwork-dev/dataproc-essentials/mongo/dev/mongo_spark_properties.json"
                    },
                    "stage":{
                        "trustStorePath": "gs://clwcirsmnp-medianetwork-stg/dataproc-essentials/mongo/stage/mongo-delta-ca",
                        "keyStorePath": "gs://clwcirsmnp-medianetwork-stg/dataproc-essentials/mongo/stage/mongo-delta.pkcs12",
                        "sparkProperties": "gs://clwcirsmnp-medianetwork-stg/dataproc-essentials/mongo/stage/mongo_spark_properties.json"
                    },
                    "prod":{
                        "trustStorePath": "gs://clwcirsmnp-medianetwork-prd/dataproc-essentials/mongo/prod/mongo-delta-ca",
                        'keyStorePath': "gs://clwcirsmnp-medianetwork-prd/dataproc-essentials/mongo/prod/mongo-delta.pkcs12",
                        "sparkProperties": "gs://clwcirsmnp-medianetwork-prd/dataproc-essentials/mongo/prod/mongo_spark_properties.json"
                    }
                }
            }
        }
    }


SPARK_JARS = {
    "gcs_bucket": {
        "dataproc": {
            "postgres":[
                "dataproc-jars/postgresql-42.7.3.jar"
            ],
            "mongo": [
                "dataproc-jars/mongo-java-driver-3.12.11.jar",
                "dataproc-jars/mongo-spark-connector-10.0.4.jar"
            ],
            "bigquery": [
                "dataproc-jars/spark-bigquery-with-dependencies_2.12-0.41.0.jar"
            ]
        },
        "composer": {
            "postgres": [
                "dataproc-jars/postgresql-42.7.3.jar"
            ],
            "mongo": [
                "dataproc-jars/mongo-java-driver-3.12.11.jar",
                "dataproc-jars/mongo-spark-connector-10.0.4.jar"
            ],
            "bigquery": [
                "dataproc-jars/spark-bigquery-with-dependencies_2.12-0.41.0.jar"
            ]
        },
        "onprem": {
            "postgres": [
                "dataproc-jars/postgresql-42.7.3.jar"
            ],
            "mongo": [
                "dataproc-jars/mongo-java-driver-3.12.11.jar",
                "dataproc-jars/mongo-spark-connector-10.0.4.jar"
            ],
            "bigquery": [
                "dataproc-jars/spark-bigquery-with-dependencies_2.12-0.41.0.jar"
            ]
        }
    },
    "maven": {
        "composer": {
            "postgres": [],
            "mongo": [],
            "bigquery": []
        },
        "on-prem": {
            "postgres": [],
            "mongo": [],
            "bigquery": []
        }
    }
}