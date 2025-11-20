import pyspark
import pyspark.sql
import logging
import os
from datetime import datetime, timedelta, date
from google.cloud import bigquery
import pytz
import pyspark.sql.functions as F
from pyspark.sql.types import *

class BaseBuildLTDBEntity:

    @classmethod
    def init_lt_db_build_class(cls, JobConfigs):
        cls.JobConfigs = JobConfigs
        cls.entity_configs = cls.JobConfigs.CHANNEL["entities"][cls.__name__]
    
        if JobConfigs.TRIGGERED_DATE_STR:
            cls.trigger_date = datetime.strptime(JobConfigs.TRIGGERED_DATE_STR, "%Y-%m-%d").date()
        else:
            cls.trigger_date = datetime.now(tz=pytz.timezone(cls.JobConfigs.TIME_ZONE)).date()
        logging.info(f"All configs for {cls.__name__} set . ")

        cls.previous_date_str = ( cls.trigger_date - timedelta(1) ).strftime(format="%Y-%m-%d")
        cls.latest_date_acceptable: date = cls.trigger_date - timedelta(1)
        cls.earliest_date_acceptable: date = datetime(year=2025, month=2, day=1, tzinfo=pytz.timezone(cls.JobConfigs.TIME_ZONE)).date()

    @classmethod
    def load_from_gcs_storage_lt(cls, spark:pyspark.sql.SparkSession):
        logging.info(f"Loading the files from GCS Location for entity: {cls.__name__} ")

        destination = os.path.join(
            "gs://", cls.JobConfigs.CHANNEL["source_bucket"],
            cls.JobConfigs.CHANNEL["gcsBaseFilepath"],
            f'{cls.entity_configs["gcsFileName"]}_{cls.trigger_date.strftime("%Y%m%d")}.csv.gz'
            )

        logging.info(f"printing file path :- {destination}")

        gcs_df: pyspark.sql.DataFrame = (
            spark.read
            .format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(destination)
        )

        gcs_df = (
            gcs_df
            .withColumn("report_start_date", F.to_date(F.col("report_start_date"), "yyyy-MM-dd"))
            .withColumn("report_end_date", F.to_date(F.col("report_end_date"), "yyyy-MM-dd"))
            .withColumn("data_refresh_date", F.to_date(F.col("data_refresh_date"), "yyyy-MM-dd"))
            .withColumn("LT_Clicks_Reporting_API", F.col("LT_Clicks_Reporting_API").cast(LongType()))
            .withColumn("LT_Impression_Reporting_API", F.col("LT_Impression_Reporting_API").cast(LongType()))
            .withColumn("LT_Clicks_Entity_API", F.col("LT_Clicks_Entity_API").cast(LongType()))
            .withColumn("LT_Impression_Entity_API", F.col("LT_Impression_Entity_API").cast(LongType()))
        )

        logging.info(f"Count of the DF: {gcs_df.count()}")
        logging.info("Print the logs loading from GCS")

        gcs_df.show(10)
        gcs_df.printSchema()
        logging.info("loading from GCS complete.")
        return gcs_df

    @classmethod
    def write_2_bq_lt(cls, dataframe: pyspark.sql.DataFrame, spark: pyspark.sql.SparkSession, table_id: str, schema: pyspark.sql.types.StructType, mode="append"):

        project_id = cls.JobConfigs.BQ_PROJECT_ID
        dataset_id = cls.JobConfigs.BQ_DATASET_ID

        dataframe.show(10)

        logging.info(f"Starting to write :-\n project: {project_id}\n dataset: {dataset_id}\n table: {table_id}")
        logging.info(f"Temporary bucket: {cls.JobConfigs.BQ_TEMPORARY_BUCKET}")
        dataframe = cls.enforce_schema(
            dataframe=dataframe, 
            spark=spark, 
            schema=schema
            )

        spark_writer = (
            dataframe.write
            .format("bigquery")
            .option("project", project_id)
            .option("dataset", dataset_id)
            .option("table", table_id)
            .mode(mode)
            .option("temporaryGcsBucket", cls.JobConfigs.BQ_TEMPORARY_BUCKET)
            .save()
        )

        logging.info("Write complete.")

    @classmethod
    def trigger_lt_db_build(cls, spark: pyspark.sql.SparkSession, JobConfigs):

        try:

            sync_report = cls.download_job_status_report(spark=spark)
            cls.write_job_status_2_bq(report=sync_report, spark=spark)
            isReportFileGenSuccessBQ = cls.isReportFileGenSuccessBQ(spark=spark, operation='lt_db_build')
            
            logging.info(f"Build begins for {cls.__name__}")
            cls.init_lt_db_build_class(JobConfigs=JobConfigs)

            audit_already_exist = cls.already_ingested(spark=spark, table_name=cls.entity_configs["auditTableId"])
            main_already_exist = cls.already_ingested(spark=spark, table_name=cls.entity_configs["mainTableId"])

            if not isReportFileGenSuccessBQ:
                raise RuntimeError(f"Cannot Trigger LT DB Build since the report gen job failed for {cls.trigger_date.strftime('%Y-%m-%d')}")

            if (audit_already_exist and main_already_exist):
                raise ValueError("Data Already Exists for both the tables.")

            new_records_df = cls.load_from_gcs_storage_lt(spark=spark)

            if not audit_already_exist:
                logging.info("Writing to Audit")
                cls.write_2_bq_lt(
                    dataframe=new_records_df,
                    spark=spark, 
                    table_id=cls.entity_configs["auditTableId"],
                    mode="append",
                    schema=cls.get_spark_schema_lt()
                    )
            
            if not main_already_exist:
                logging.info("Writing to Main")
                cls.write_2_bq_lt(
                    dataframe=new_records_df,
                    spark=spark, 
                    table_id=cls.entity_configs["mainTableId"],
                    mode="overwrite",
                    schema=cls.get_spark_schema_lt()
                    )
            isSuccess=True
            build_status_message = "Build Successful"
            logging.info("New data successfully read from gcs path.")

        except Exception as e:

            logging.error(f"Job Failed for {cls.__name__} DB Build.")
            isSuccess=False
            build_status_message = f"{type(e).__name__}:{e}"
            logging.error(build_status_message)

        finally:
            
            report = cls.generate_job_report(
                start_date=cls.earliest_date_acceptable,
                end_date=cls.latest_date_acceptable,
                trigger_date=cls.trigger_date,
                isSuccess=isSuccess,
                operation_name="lt_db_build",
                message=build_status_message
            )

            cls.write_job_status_2_bq(
                report=report,
                spark=spark
            )
            logging.info(f"Build complete for {cls.__name__}")