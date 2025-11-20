from pyspark.sql.types import *
from typing import Optional, Union
from datetime import datetime
import os
# import logging
import pyspark
from pyspark.sql import functions as F
import pandas as pd
from delta_sdk.utils import logging

class JobStatusReport:

    @classmethod
    def get_job_status_report_spark_schema(cls) -> StructType:
        
        schema_fields = [
            StructField("startDate", DateType(), False),
            StructField("endDate", DateType(), False),
            StructField("jobRunDate", DateType(), False),
            StructField("operation", StringType(), False),
            StructField("entityType", StringType(), False),
            StructField("isSuccess", BooleanType(), False),
            StructField("message", StringType(), False),
        ]

        return schema_fields

    @classmethod
    def gam_job_status_file_destination(
        cls,
        ):
        return  os.path.join(
            "gs://",
            cls.JobConfigs.CHANNEL["source_bucket"],
            cls.JobConfigs.CHANNEL["gcsBaseFilepath"],
            f'{cls.JOB_STATUS_REPORT_TABLE}.csv.gz'
            )

    @classmethod
    def generate_job_report(
        cls,
        isSuccess: bool,
        operation_name: str,
        message: str = '',
        entity: str = 'entity',
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        trigger_date: Optional[datetime.date] = None,
    ):
        start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
        end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None
        trigger_date_str = trigger_date.strftime("%Y-%m-%d") if end_date else None

        record = dict(
                startDate=start_date_str,
                endDate=end_date_str,
                jobRunDate=trigger_date_str,
                operation=operation_name,
                entityType=entity,
                isSuccess=int(bool(isSuccess)),
                message=message
            )

        logging.info("Log the status report.")
        logging.info(record)
        return record
    
    @classmethod
    def write_job_status_2_bq(
        cls,
        report: Union[dict, pyspark.sql.DataFrame],
        spark: pyspark.sql.SparkSession
    ):

        if isinstance(report, dict):
            report = (
                spark
                .createDataFrame(data=report)
                .withColumn("startDate", F.to_date(F.col("startDate"), "yyyy-MM-dd"))
                .withColumn("endDate", F.to_date(F.col("endDate"), "yyyy-MM-dd"))
                .withColumn("jobRunDate", F.to_date(F.col("jobRunDate"), "yyyy-MM-dd"))
            )

        (
            report.write
            .format("bigquery")
            .option("table", cls.JobConfigs.JOB_STATUS_REPORT_TABLE)
            .mode("append")
            .option("temporaryGcsBucket", cls.JobConfigs.BQ_TEMPORARY_BUCKET)
            .save()
        )
        logging.info(f"Job status logged to :-{cls.JobConfigs.JOB_STATUS_REPORT_TABLE}")

    @classmethod
    def upload_job_status_report(
        cls,
        storage_conns,
        report: Union[pyspark.sql.DataFrame, pd.DataFrame, dict]
    ):

        if isinstance(report, pyspark.sql.DataFrame):
            report = report.toPandas()
        elif isinstance(report, dict):
            report = pd.DataFrame(data=report, index=[0])

        file_name = cls.JobConfigs.JOB_STATUS_REPORT_FILE_NAME.replace('<EntityLevel>',cls.__name__)
        source = os.path.join(cls.JobConfigs.CHANNEL["localDownloadFilePath"], file_name)
        destination = os.path.join(cls.JobConfigs.CHANNEL["gcsBaseFilepath"], file_name)

        logging.info(f"Source: {source}")
        logging.info(f"Destination: {destination}")
        report.to_csv(source, index=False, compression='gzip', encoding='utf-8')

        for storage_conn in storage_conns:
            storage_conn.upload_file(source=source, destination=destination, content_type="application/octet-stream")
            logging.info(f"Uploaded to Storage {storage_conn.bucket_name}: {destination}")
        logging.info(f"Dataframe written to local path: {source}")

        return destination

    @classmethod
    def download_job_status_report(
        cls, 
        spark:pyspark.sql.SparkSession
        ):
        logging.info(f"Loading the files from GCS Location for entity: {cls.__name__} ")

        destination = os.path.join(
            "gs://",
            cls.JobConfigs.CHANNEL["source_bucket"],
            cls.JobConfigs.CHANNEL["gcsBaseFilepath"],
            cls.JobConfigs.JOB_STATUS_REPORT_FILE_NAME.replace('<EntityLevel>',cls.__name__)
            )

        logging.info(f"printing file path :- {destination}")

        record_df: pyspark.sql.DataFrame = (
            spark.read
            .format("csv")
            .option("header", "true")
            .schema(schema=cls.get_job_status_report_spark_schema())
            .load(path=destination)
        )

        logging.info(f"Count of the DF: {record_df.count()}")
        logging.info("Print the logs loading from GCS")
        
        record = record_df.toPandas().to_dict()
        logging.info(record)
        return record
    
    @classmethod
    def isReportFileGenSuccessBQ(
        cls, 
        spark: pyspark.sql.SparkSession,
        operation: str
        ):
        try:
            table_ref = f"{cls.JobConfigs.BQ_PROJECT_ID}.{cls.JobConfigs.BQ_DATASET_IDtaset_id}.{cls.JOB_STATUS_REPORT_TABLE}"
            logging.info(f"Checking the status of the report Generation for {operation} of entity {cls.__name__} on {cls.trigger_date.strftime('%Y-%m-%d')}")

            status = (
                spark
                .read
                .format("bigquery")
                .option("table", table_ref)
                .load()
                .filter( 
                    F.col("data_refresh_date") == cls.trigger_date & 
                    F.col("entityType") == cls.__name__ &
                    F.col("operation") == operation
                )
                .select("isSuccess")
                .first()
            )

            if status and status["isSucces"]:
                logging("Report Generation job was successful.")
                return True
            else:
                logging("Report Generation job Failed.")
                return False

        except Exception as e:
            logging.error("Job Status Fetch failed.")
            logging.error(f"{type(e)}:{e}")
            return False