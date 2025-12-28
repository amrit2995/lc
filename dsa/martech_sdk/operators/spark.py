from martech_sdk.utils import logging
import pyspark
from pyspark.sql import SparkSession, DataFrame
from martech_sdk.configs.env import EnvConfig
from martech_sdk.configs.datasets import Dataset
from martech_sdk.configs.common import CommonConfigs


############################################# Enums #############################################

class SparkWriteMode:
    APPEND = 'append'
    OVERWRITE = 'overwrite'

class SparkFormat:
    BIGQUERY = 'bigquery'
    GCS = 'gcs'
    CSV = 'csv'
    PARQUET = 'parquet'
    ORC = 'orc'

class SparkBQWriteMode:
    APPEND = 'append'
    OVERWRITE = 'overwrite'

############################################# Spark Operator #############################################

class SparkOperator:
    _session = None
    app_name = 'martech-sdk-default-app'
    materialization_dataset = Dataset.MARTECH_TEMP
    temporary_gcs_bucket = EnvConfig.BUCKET.TMP
    materialization_dataset_expiry_in_minutes = CommonConfigs.DEFAULT_DATASET_EXPIRY_IN_MINS

    @classmethod
    def enforce_schema(cls, dataframe: pyspark.sql.DataFrame, schema: pyspark.sql.types.StructType):
        logging.info("schema before")
        dataframe.printSchema()
        dataframe.show(10)

        columns_list = [field.name for field in schema.fields]
        dataframe = dataframe.select(columns_list)
        dataframe = cls._session.createDataFrame(dataframe.rdd, schema)

        logging.info("schema after")
        dataframe.printSchema()
        dataframe.show(10)
        logging.info("schema enforced.")
        return dataframe

    @classmethod
    def create_session(cls):

        logging.info(f"App name: {cls.app_name}")
        logging.info(f"Materialization dataset: {cls.materialization_dataset}")
        logging.info(f"Temporary GCS bucket: {cls.temporary_gcs_bucket}")
        logging.info(f"Materialization dataset expiry in minutes: {cls.materialization_dataset_expiry_in_minutes}")

        logging.info("Creating Spark session...")

        spark_session = SparkSession.builder.appName(cls.app_name).getOrCreate()
        spark_session.sparkContext.setLogLevel("ERROR")
        spark_session.conf.set("spark.datasource.bigquery.intermediateFormat", "orc")
        spark_session.conf.set("viewsEnabled", "true")
        spark_session.conf.set("materializationDataset", cls.materialization_dataset)
        spark_session.conf.set("temporaryGcsBucket", cls.temporary_gcs_bucket)

        if cls.materialization_dataset_expiry_in_minutes:
            spark_session.conf.set("materializationExpirationTimeInMinutes", cls.materialization_dataset_expiry_in_minutes)

        logging.info(f"Spark Version: {spark_session.version}")
        logging.info("Spark session created.")

        return spark_session

    @classmethod
    def get_session(
        cls,
        app_name: str = '',
        materialization_dataset: str | Dataset = '',
        temporary_gcs_bucket: str = '',
        materialization_dataset_expiry_in_minutes: str = ''
        ):

        if app_name:
            cls.app_name = app_name
        else:
            cls.app_name = 'martech-sdk-default-app'
        logging.info(f"App name set to: {cls.app_name}")

        if materialization_dataset:
            cls.materialization_dataset = materialization_dataset
        else:
            cls.materialization_dataset = Dataset.MARTECH_TEMP
        logging.info(f"Materialization dataset set to: {cls.materialization_dataset}")

        if temporary_gcs_bucket:
            cls.temporary_gcs_bucket = temporary_gcs_bucket
        else:
            cls.temporary_gcs_bucket = EnvConfig.BUCKET.TMP
        logging.info(f"Temporary GCS bucket set to: {cls.temporary_gcs_bucket}")

        if materialization_dataset_expiry_in_minutes:
            cls.materialization_dataset_expiry_in_minutes = materialization_dataset_expiry_in_minutes
        else:
            cls.materialization_dataset_expiry_in_minutes = CommonConfigs.DEFAULT_DATASET_EXPIRY_IN_MINS
        logging.info(f"Materialization dataset expiry in minutes set to: {cls.materialization_dataset_expiry_in_minutes}")

        if not cls._session:
            cls._session = cls.create_session()
        logging.info("Returning Spark session.")
        return cls._session

    @classmethod
    def read_from_bq(
        cls,
        query: str, 
        query_filter: str = None
    ):

        logging.info("Reading data from BigQuery...")
        logging.info("Query:-")
        logging.info(query)

        bq_query = (
            cls._session
            .read
            .format(SparkFormat.BIGQUERY)
            .option("query", query)
            )

        if query_filter:
            bq_query = bq_query.option("filter", query_filter)

        logging.info("Data read from BigQuery successfully..")  
        return bq_query.load()

    @classmethod
    def write_to_bq(
        cls,
        data_df: DataFrame, 
        table_name: str, 
        dataset_name: str,
        mode: str = SparkBQWriteMode.APPEND
    ):
        logging.info(f"Dataframe count: {data_df.count()}")
        logging.info(f"Dataframe schema: {data_df.schema}")
        logging.info(f"Dataframe example:")
        data_df.show(5)
        logging.info(f"Writing data to BigQuery table: {table_name}")

        if not dataset_name:
            dataset_name = cls.materialization_dataset
        (
            data_df
            .write
                .format(SparkFormat.BIGQUERY)
                .option("dataset", dataset_name)
                .option("table", table_name)
                .mode(mode)
                .save()
            )
        
        logging.info(f"Data written to BigQuery table: {table_name}")