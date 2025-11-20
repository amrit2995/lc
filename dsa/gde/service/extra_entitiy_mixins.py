import pyspark
from pyspark.sql import functions as F
from datetime import datetime
from typing import Optional
from delta_sdk.utils import logging
import pyspark.sql
import os
from pyspark.sql.types import *
from typing import Union
import pandas as pd

class ExtraEntityMixins:

    @classmethod
    def enforce_schema(cls, dataframe: pyspark.sql.DataFrame, spark: pyspark.sql.SparkSession, schema: pyspark.sql.types.StructType):
        logging.info("schema before")
        dataframe.printSchema()
        dataframe.show(10)

        columns_list = [field.name for field in schema.fields]
        dataframe = dataframe.select(columns_list)
        dataframe = spark.createDataFrame(dataframe.rdd, schema)

        logging.info("schema after")
        dataframe.printSchema()
        dataframe.show(10)
        logging.info("schema enforced.")
        return dataframe


    @classmethod
    def already_ingested(cls, spark: pyspark.sql.SparkSession, table_name: str):

        try:

            project_id = cls.JobConfigs.BQ_PROJECT_ID
            dataset_id = cls.JobConfigs.BQ_DATASET_ID
            table_ref = f"{project_id}.{dataset_id}.{table_name}"

            logging.info(f"Checking if values for trigger date {cls.trigger_date.strftime('%Y-%m-%d')} already exists in {table_ref}")

            date_count = (
                spark
                .read
                .format("bigquery")
                .option("table", table_ref)
                .load()
                .filter( F.col("data_refresh_date") == cls.trigger_date)
                .select("data_refresh_date")
                .first()
            )

            if date_count:
                logging.info(date_count)
                logging.info(f"Data for {cls.trigger_date.strftime('%Y-%m-%d')} already ingested for the table {table_ref} ")
                return True
            else:
                logging.info(f"Data for {cls.trigger_date.strftime('%Y-%m-%d')} does not exist yet for the table {table_ref}")
                return False
        except Exception as e:
            logging.error(f"{type(e).__name__}: {e}")
            return False