# from pyspark.sql import SparkSession
import os
from datetime import datetime, timedelta
from datetime import datetime, timedelta, date
import pyspark.sql
import pyspark
import pyspark.sql.types
import pytz
from google.cloud import bigquery
from pyspark.sql.types import *
from pyspark.sql import functions as F
from delta_sdk.utils import logging

class BaseBuildDBEntity:

    @classmethod
    def get_spark_schema(cls, *args, **kwargs):
        logging.error(f"No schema defined for the entity {cls.__name__}")

    @classmethod
    def init_class(cls, JobConfigs):
        cls.JobConfigs = JobConfigs
        cls.entity_configs = cls.JobConfigs.CHANNEL["entities"][cls.__name__]["report"]

        if JobConfigs.TRIGGERED_DATE_STR:
            cls.trigger_date = datetime.strptime(JobConfigs.TRIGGERED_DATE_STR, "%Y-%m-%d").date()
        else:
            cls.trigger_date: date = datetime.now(tz=pytz.timezone(cls.JobConfigs.TIME_ZONE)).date()

        gam_fetch_date_range = int(cls.JobConfigs.CHANNEL["gam_fetch_date_range"])
        cls.build_end_date: date = cls.trigger_date - timedelta(1)
        cls.build_start_date: date = cls.trigger_date - timedelta(days=gam_fetch_date_range)

        cls.old_records_start_date_str: str = cls.build_start_date.strftime("%Y-%m-%d")
        cls.old_records_end_date_str: str = (cls.build_end_date - timedelta(1)).strftime("%Y-%m-%d")
        logging.info(f"All configs for {cls.__name__} set . ")

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
    def custom_load_gcs_transformations(cls, df, spark):
        return df

    @classmethod
    def load_from_gcs_storage(cls, spark: pyspark.sql.SparkSession):

        logging.info(f"Loading the files from GCS Location for entity: {cls.__name__} ")

        destination = os.path.join(
            "gs://", cls.JobConfigs.CHANNEL["source_bucket"],
            cls.JobConfigs.CHANNEL["gcsBaseFilepath"],
            cls.trigger_date.strftime("%Y%m%d"),
            cls.entity_configs['pg']['gcsFilesName']
            )

        logging.info(f"printing file path :- {destination}")

        gcs_df: pyspark.sql.DataFrame = (
            spark.read
            .format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(destination)
        )
        final_column_name = list(set(cls.entity_configs["pg"]["final_main_columns"]) - set(["discrepancy_found", "discrepancy_fields"]))
        logging.info(f"Final columns list: {final_column_name}")
        gcs_df = cls.custom_load_gcs_transformations(gcs_df, spark, final_column_name=final_column_name)

        logging.info(f"Count of the DF: {gcs_df.count()}")
        logging.info("Print the logs loading from GCS")

        gcs_df.show(10)
        gcs_df.printSchema()
        cls.daywise_counts(gcs_df)
        return gcs_df
    
    @classmethod
    def read_old_main_records(cls, spark: pyspark.sql.SparkSession):

        project_id = cls.JobConfigs.CHANNEL["projectId"]
        dataset_id = cls.JobConfigs.CHANNEL["bqDataset"]

        logging.info("Read old records from the BQ.")

        table_id = cls.entity_configs["pg"]["mainTableId"]

        logging.info(f"For trigger date: {cls.trigger_date.strftime('%Y-%m-%d')} \n \
                    Fetching old records in range {cls.old_records_start_date_str} and {cls.old_records_end_date_str}")

        query = f"""
            SELECT * FROM `{project_id}.{dataset_id}.{table_id}`
            WHERE report_date BETWEEN DATE '{cls.old_records_start_date_str}' AND DATE '{cls.old_records_end_date_str}'
        """

        filter = f"report_date BETWEEN DATE '{cls.old_records_start_date_str}' AND DATE '{cls.old_records_end_date_str}'"
        logging.info(f"filter added :- {filter}")

        old_bq_df: pyspark.sql.DataFrame = (
            spark.read
            .format("bigquery")
            .option("table", f"{project_id}.{dataset_id}.{table_id}")
            .option("filter", filter)
            .load()
        )

        final_column_name = list(set(cls.entity_configs["pg"]["final_main_columns"]) - set(["discrepancy_found", "discrepancy_fields"]))
        old_bq_df = cls.custom_load_gcs_transformations(old_bq_df, spark, final_column_name)
        logging.info(f"Count of the DF: {old_bq_df.count()}")
        logging.info("Print the logs loading from BQ")

        old_bq_df.show(10)
        old_bq_df.printSchema()

        cls.daywise_counts(old_bq_df)

        return old_bq_df

    @classmethod
    def write_2_bq(cls, dataframe: pyspark.sql.DataFrame, spark: pyspark.sql.SparkSession, table_id: str, schema: pyspark.sql.types.StructType):

        project_id = cls.JobConfigs.CHANNEL["projectId"]
        dataset_id = cls.JobConfigs.CHANNEL["bqDataset"]

        dataframe.show(10)

        logging.info(f"Starting to write :-\n project: {project_id}\n dataset: {dataset_id}\n table: {table_id}")
        logging.info(f"Temporary bucket: {cls.JobConfigs.BQ_TEMPORARY_BUCKET}")
        dataframe = cls.enforce_schema(dataframe=dataframe, spark=spark, schema=schema)
        cls.daywise_counts(dataframe)
        spark_writer = (
            dataframe.write
            .format("bigquery")
            .option("project", project_id)
            .option("dataset", dataset_id)
            .option("table", table_id)
            .mode("append")
            .option("temporaryGcsBucket", cls.JobConfigs.BQ_TEMPORARY_BUCKET)
            .save()
        )

        logging.info("Write complete.")

    @classmethod
    def delete_from_bq(cls):

        logging.info("delete records for the existing date range.")

        client = bigquery.Client()

        project_id = cls.JobConfigs.CHANNEL["projectId"]
        dataset_id = cls.JobConfigs.CHANNEL["bqDataset"]
        table_id = cls.entity_configs["pg"]["mainTableId"]

        logging.info(f"For trigger date: {cls.trigger_date.strftime('%Y-%m-%d')} \n \
                    Deleting old records in range {cls.old_records_start_date_str} and {cls.old_records_end_date_str}")

        query = f"""
            DELETE FROM `{project_id}.{dataset_id}.{table_id}`
            WHERE report_date BETWEEN DATE '{cls.old_records_start_date_str}' AND DATE '{cls.old_records_end_date_str}'
        """

        logging.info(f"Query:-\n {query}")

        try:
            query_job = client.query(query)
            query_job.result()
            logging.info("Deletion completed successfully.")
        except Exception as e:
            logging.error(f"Error during deletion: {str(e)}")
            raise

    @classmethod
    def merge_old_new_df(cls, old_records_df: pyspark.sql.DataFrame, new_records_df: pyspark.sql.DataFrame, spark: pyspark.sql.SparkSession):
        """
        Merges old and new records in a PySpark DataFrame, updating records where needed.
        """
        
        logging.info("Merges old and new records in a PySpark DataFrame, updating records where needed.")

        final_column_name = cls.entity_configs["pg"]["final_main_columns"]
        columns_to_match = cls.entity_configs["pg"]["columns_to_match"]
        columns_to_update = list(set(final_column_name) - set(columns_to_match) - set(["discrepancy_found","discrepancy_fields"]))
        overwrite = cls.JobConfigs.CHANNEL["overwrite_data_in_main"]
        
        logging.info(f" final_column_name:- {final_column_name}")
        logging.info(f" columns_to_match:- {columns_to_match}")

        logging.info(f" overwrite:- {overwrite}")

        if old_records_df.count() == 0:
            logging.info("No existing records for the range of Report Dates")

            new_records_df = (
                new_records_df
                .withColumn("discrepancy_fields", F.lit(""))
                .withColumn("discrepancy_found", F.lit(0))
                .withColumn("data_refresh_date", F.to_date(F.lit(cls.trigger_date), "yyyy-MM-dd"))
            )

            logging.info(f"final records when old is null :-\n length: {new_records_df.count()}\n Columns:-{new_records_df.columns}")
            new_records_df.show(5)

            return new_records_df

        new_records_df = new_records_df.select(
            *columns_to_match,
            *(F.col(x).alias('new_'+x) for x in columns_to_update)
        )

        logging.info(f"new_records_df before merge:-\n length: {new_records_df.count()}\n Columns:-{new_records_df.columns}")
        new_records_df.show(10)
        new_records_df.printSchema()

        old_records_df = old_records_df.select(
            *columns_to_match,
            *(F.col(x).alias('old_'+x) for x in columns_to_update)
        )

        logging.info(f"old_records_df before merge:-\n length: {old_records_df.count()}\n Columns:-{old_records_df.columns}")
        old_records_df.show(10)
        old_records_df.printSchema()

        merged_df = old_records_df.join(
            other=new_records_df, 
            on=columns_to_match, 
            how="outer"
        )

        logging.info(f"Merged Old-New records:- {merged_df.columns} length: {merged_df.count()}\n Columns:-{merged_df.columns} ")
        merged_df.show(10)
        merged_df.printSchema()

        logging.info(f"{columns_to_update} updation begins.")

        merged_df = (
            merged_df
            # .withColumn("discrepancy_fields", F.expr("ARRAY<STRING>[]"))
            .withColumn("discrepancy_fields", F.array())
            .withColumn("discrepancy_found", F.lit(0))
        )

        for col_name in columns_to_update:

            val_new = F.col(f"new_{col_name}")
            val_old = F.col(f"old_{col_name}")

            if col_name in ("impressions", "clicks", "ctr", "total_revenue"):
                updated_val = (
                    F.when(F.isnull(val_new), val_old)
                    .when(F.isnull(val_old), val_new)
                    .when(val_new >= val_old, val_new)
                    .when((val_new < val_old) & F.lit(overwrite)==True, val_new)
                    .otherwise(val_old)
                )

                merged_df = merged_df.withColumn(
                    "discrepancy_fields",
                    F.when(
                        (val_new.isNotNull() & val_old.isNotNull() & (val_new < val_old)),
                        F.array_union(F.col("discrepancy_fields"), F.array(F.lit(col_name)))
                    ).otherwise(F.col("discrepancy_fields"))
                )
            else:
                updated_val = (
                    F.when(F.isnull(val_new), val_old)
                    .otherwise(val_new)
                )

            merged_df = merged_df.withColumn(col_name, updated_val)
            logging.info(f"Col:- {col_name} updated")

        logging.info(f" records after updating {columns_to_update} fields :- {merged_df.columns}")
        merged_df.show(10)

        logging.info("Starting to set the discrepancy fields.")
        merged_df = (
            merged_df
            .withColumn("discrepancy_fields", F.array_join(F.col("discrepancy_fields"), ","))
            .withColumn("discrepancy_found", F.when(F.col("discrepancy_fields") != "", F.lit(1)).otherwise(F.lit(0)))
            .withColumn("data_refresh_date", F.to_date(F.lit(cls.trigger_date), "yyyy-MM-dd"))
        )
        logging.info("discrepancy_found field set.")
        logging.info(f"{columns_to_update} discrepancy fields updated successfully.")

        final_df = merged_df.select(final_column_name)
        logging.info("Dataframe after merge:-")
        final_df.show(10)
        cls.daywise_counts(final_df)
        final_df.printSchema()

        return final_df

    @classmethod
    def job_report_bq(cls, spark: pyspark.sql.SparkSession, isSuccess: bool, operation_name: str, message: str = ''):

        table_name = cls.JobConfigs.CHANNEL["job_status_report_table_name"]
        project_id = cls.JobConfigs.CHANNEL["projectId"]
        dataset_id = cls.JobConfigs.CHANNEL["bqDataset"]
        table_ref = f"{project_id}.{dataset_id}.{table_name}"
        logging.info(f"Table name: {table_ref}")

        record = [
            (
                cls.build_start_date.strftime("%Y-%m-%d"),
                cls.build_end_date.strftime("%Y-%m-%d"),
                cls.trigger_date.strftime("%Y-%m-%d"),
                operation_name,
                cls.__name__,
                int(bool(isSuccess)),
                message
            )
        ]

        logging.info("Log the status report.")
        logging.info(record)

        schema = ["startDate", "endDate", "jobRunDate", "operation", "entityType", "isSuccess", "message"]

        df = (
            spark
            .createDataFrame(record, schema=schema)
            .withColumn("startDate", F.to_date(F.col("startDate"), "yyyy-MM-dd"))
            .withColumn("endDate", F.to_date(F.col("endDate"), "yyyy-MM-dd"))
            .withColumn("jobRunDate", F.to_date(F.col("jobRunDate"), "yyyy-MM-dd"))
        )

        (
            df.write
            .format("bigquery")
            .option("table", table_ref)
            .mode("append")
            .option("temporaryGcsBucket", cls.JobConfigs.BQ_TEMPORARY_BUCKET)
            .save()
        )
        logging.info(f"Job status written to BigQuery: {record}")

    @classmethod
    def daywise_counts(cls, df: pyspark.sql.DataFrame):
        logging.info("Daywise count of rows by report_date and data_refresh_date.")
        grouped_df = (
            df
            .groupby("data_refresh_date", "report_date")
            .count()
        )
        grouped_df.show()


    @classmethod
    def trigger_db_build(cls, spark: pyspark.sql.SparkSession, JobConfigs):

        try:
            logging.info(f"Build begins for {cls.__name__}")
            cls.init_class(JobConfigs=JobConfigs)

            # audit_already_exist = cls.already_ingested(spark=spark, table_name=cls.entity_configs["pg"]["auditTableId"])
            # main_already_exist = cls.already_ingested(spark=spark, table_name=cls.entity_configs["pg"]["mainTableId"])

            new_records_df = cls.load_from_gcs_storage(spark=spark)
            logging.info("New data successfully read from gcs path.")
            # if not audit_already_exist:
            cls.write_2_bq(
                dataframe=new_records_df, 
                spark=spark, 
                table_id=cls.entity_configs["pg"]["auditTableId"], 
                schema=cls.get_spark_schema("audit")
                ) 

            # if not main_already_exist:
            old_records_df = cls.read_old_main_records(spark=spark)
            final_main_df = cls.merge_old_new_df(old_records_df=old_records_df, new_records_df=new_records_df, spark=spark).cache()

            cls.delete_from_bq()
            logging.info("after the merge is complete.")
            cls.daywise_counts(final_main_df)
            cls.write_2_bq(
                dataframe=final_main_df, 
                spark=spark, 
                table_id=cls.entity_configs["pg"]["mainTableId"], 
                schema=cls.get_spark_schema("main")
                )
            isSuccess=True
            build_status_message = "Build Successful"

        except Exception as e:
            logging.error(f"Job Failed for {cls.__name__} DB Build.")
            isSuccess=False
            build_status_message = f"{type(e).__name__}:{e}"
            logging.error(build_status_message)

        finally:
            cls.job_report_bq(
                spark=spark,
                isSuccess=isSuccess,
                operation_name="api_db_build",
                message=build_status_message
                )

            logging.info(f"Build complete for {cls.__name__}")