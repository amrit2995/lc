import os
import json
from pyspark.sql import SparkSession
from delta_sdk.connectors.cloud.gcp.storage import GCSStorageConnector
from delta_sdk.connectors.dao.mongo import MongoConnector
from delta_sdk.connectors.dao import DBType
from delta_sdk.utils import logging
from delta_sdk.configs.common import InfraType, SPARK_JARS, CERTS
from delta_sdk.configs.connConfigs import GCP_PROJECT_MAPPING
from delta_sdk.connectors.dao import DBType

class JarSource:
    GCS_BUCKET = 'gcs_bucket'
    MAVEN = 'maven'

class SparkUtils:

    @staticmethod
    def get_default_spark_builder(infra_type, db_types: list=[], jar_source=JarSource.GCS_BUCKET, env: str='', nucleusHash='', dataprocNucleusHash='', base_dir='', clusterName='', download_jars=False) -> SparkSession:

        spark_builder = (
            SparkSession.builder
            .appName(f"SparkSession{''.join(db_types)}")
        )
        logging.info('Created default spark builder.')

        gcs_connector = GCSStorageConnector(env=env, nucleusHash=nucleusHash)

        if jar_source == JarSource.GCS_BUCKET:

            spark_jars = SparkUtils.get_spark_jars(
                jar_source=JarSource.GCS_BUCKET, 
                db_types=db_types,
                infra_type=infra_type, 
                download_to_local=download_jars, 
                gcs_connector=gcs_connector, 
                base_dir=base_dir
                )

            spark_builder = spark_builder.config('spark.jars', ','.join(spark_jars))
            logging.info(f"Adding the local spark jars to the spark config :- \n {spark_jars}")

        else:
            maven_spark_jars = []
            for db_type in db_types:
                maven_spark_jars += SPARK_JARS[JarSource.MAVEN][db_type]
            
            spark_builder = spark_builder.config('spark.jars.packages', ','.join(maven_spark_jars))
            logging.info(f"Adding all the maven spark jar urls to the spark config:- {maven_spark_jars}")

        if DBType.MONGO in db_types:
            if infra_type in [InfraType.COMPOSER, InfraType.ON_PREM]:

                mongo_conn = MongoConnector(env=env, nucleusHash=nucleusHash, clusterName=clusterName)
                mongo_creds = mongo_conn.get_mongo_creds()
                trustStorePassword, keyStorePassword = mongo_creds.truststore_code, mongo_creds.keystore_code
                mongo_props = None

                gcs_truststore_cert_path = CERTS[JarSource.GCS_BUCKET][DBType.MONGO]['delta'][env]['trustStorePath']
                gcs_keystore_cert_path = CERTS[JarSource.GCS_BUCKET][DBType.MONGO]['delta'][env]['keyStorePath']
                gcs_mongo_spark_props_path = CERTS[JarSource.GCS_BUCKET][DBType.MONGO]['delta'][env]['sparkProperties']
                
                local_truststore_cert_path = os.path.join(base_dir, gcs_truststore_cert_path.split('/')[-1])
                local_keystore_cert_path = os.path.join(base_dir, gcs_keystore_cert_path.split('/')[-1])
                local_mongo_spark_props_path = os.path.join(base_dir, gcs_mongo_spark_props_path.split('/')[-1])

                gcs_connector.download_file(source=gcs_truststore_cert_path, destination=local_truststore_cert_path)
                gcs_connector.download_file(source=gcs_keystore_cert_path, destination=local_keystore_cert_path)
                gcs_connector.download_file(source=gcs_mongo_spark_props_path, destination=local_mongo_spark_props_path)

                logging.info(f"Downloaded the mongo certs and properties:- {local_truststore_cert_path, local_keystore_cert_path, local_mongo_spark_props_path}")

                with open(local_mongo_spark_props_path) as file:
                    mongo_props = json.load(file)['mongo_cert_properties']
                
                for prop in ['spark.driver.extraJavaOptions', 'spark.executor.extraJavaOptions']:
                    mongo_props[prop] = (
                        mongo_props[prop]
                        .replace('<TRUSTSTORE_CERT_PATH>', local_truststore_cert_path)
                        .replace('<TRUSTSTORE_CODE>', trustStorePassword)
                        .replace('<KEYSTORE_CERT_PATH>', local_keystore_cert_path)
                        .replace('<KEYSTORE_CODE>', keyStorePassword)
                    )

                for key, value in mongo_props.items():
                    spark_builder = spark_builder.config(key, value)

                spark_builder = spark_builder.config('spark.files', ','.join([local_truststore_cert_path, local_truststore_cert_path]))

            spark_builder = (
                spark_builder
                .config("spark.mongodb.read.connection.uri", mongo_creds.host)
                .config("spark.mongodb.write.connection.uri", mongo_creds.host)
            )

        if DBType.BIGQUERY in db_types:
            if infra_type in [InfraType.COMPOSER, InfraType.ON_PREM]:

                if not dataprocNucleusHash:
                    ValueError("Mandatory param 'dataprocNucleusHash' not provided.")

                gcs_dataproc_conn = GCSStorageConnector(env=env, nucleusHash=dataprocNucleusHash, composer=True)
                gcs_cred_file_path = gcs_dataproc_conn.get_gcs_creds(file_path=True)

                spark_builder = (
                    spark_builder
                    .config("parentProject", GCP_PROJECT_MAPPING[env])
                    .config("credentialsFile", gcs_cred_file_path)
                )

        spark = spark_builder.getOrCreate()
        logging.info("Spark session created")
        logging.info("Below are the spark configs of the spark session .")
        logging.info(spark.sparkContext.getConf().getAll())

        return spark
    
    @staticmethod
    def get_spark_jars(jar_source, infra_type, db_types: list, gcs_connector: GCSStorageConnector, download_to_local=False, base_dir=''):

        spark_jars = []

        if jar_source == JarSource.MAVEN:
            for db_type in db_types:
                spark_jars += SPARK_JARS[JarSource.MAVEN][infra_type][db_type]

        elif jar_source == JarSource.GCS_BUCKET:
            for db_type in db_types:
                spark_jars += SPARK_JARS[JarSource.GCS_BUCKET][infra_type][db_type]

            if download_to_local == True:
                local_spark_jars = []
                for spark_jar in spark_jars:
                    spark_jar_name = spark_jar.split('/')[-1]
                    source = spark_jar
                    destination = os.path.join(base_dir, spark_jar_name)
                    gcs_connector.download_file(source=source, destination=destination)
                    local_spark_jars.append(destination)
                spark_jars = local_spark_jars
            
            else:
                spark_jars = [gcs_connector.get_absolute_gsutil_path(spark_jar) for spark_jar in spark_jars]

        return spark_jars