from delta_sdk.utils import logging
from googleads import ad_manager
import os
import pyspark.sql
from gam_daci_etl.configs import JobConfigs
from datetime import datetime, date, timedelta
from delta_sdk.utils.common import RateLimiter, CommonUtils
from pyspark.sql.types import *
from pyspark.sql import functions as F
import pytz
import zeep
import pyspark
import zeep
import tempfile
import pytz
import copy

class BaseLTServiceEntity:

    @classmethod
    def init_lt_class(cls):
        cls.gam_pagination_limit = 500
        cls.gam_batch = 0
        cls.JobConfigs = JobConfigs
        cls.trigger_date  =  datetime.now(tz=pytz.timezone(cls.JobConfigs.TIME_ZONE)).date()
        cls.latest_date_acceptable: date = cls.trigger_date - timedelta(1)
        cls.earliest_date_acceptable: date = datetime(year=2025, month=2, day=1, tzinfo=pytz.timezone(cls.JobConfigs.TIME_ZONE)).date()

        if JobConfigs.TRIGGERED_DATE_STR:
            cls.trigger_date = datetime.strptime(JobConfigs.TRIGGERED_DATE_STR, "%Y-%m-%d").date()
        else:
            cls.trigger_date = datetime.now(tz=pytz.timezone(cls.JobConfigs.TIME_ZONE)).date()

    @classmethod
    def post_entity_lt_processing(cls, spark, df, *args, **kwargs):
        return df

    @classmethod
    def build_gam_lt_service_api_statement(cls):

        statement: ad_manager.StatementBuilder = copy.deepcopy(
            (
                ad_manager
                .StatementBuilder(version=cls.JobConfigs.GAM_VERSION)
                .Where(
                    "startDateTime >= :startDateTime "
                )
                .WithBindVariable('startDateTime', cls.earliest_date_acceptable.isoformat())
            )
        )
        return statement
    
    @classmethod
    def build_gam_lt_report_api_statement(cls):

        advertiserFilters = cls.JobConfigs.CHANNEL["advertiserFilters"]

        statement: ad_manager.StatementBuilder = copy.deepcopy(
            (
                ad_manager
                .StatementBuilder(version=cls.JobConfigs.GAM_VERSION)
            )
        )
        return statement

    @classmethod
    @CommonUtils.retry_connection(
        max_retries=4, delay=1, delay_type='exponential',
        rate_limiter=RateLimiter(
            name='gam_lt_service', mode=RateLimiter.mode.BY_CEILING,
            ceiling=15, time_window=60
            ))
    def fetch_service(cls, gam_client=None,  *args, **kwargs):
        """Fetch records for respective entities from GAM.
        Args::
            gam_client
        Response::
            Yielding records in batches as configured.
        Note::
        """
        logging.info("inside 'fetch' block.")

        service = gam_client.GetService(service_name=cls.gam_service_name, version=JobConfigs.GAM_VERSION)

        cls.start_date: datetime = datetime(2022, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(JobConfigs.TIME_ZONE))
        cls.end_date: datetime = datetime.now(tz=pytz.timezone(JobConfigs.TIME_ZONE))

        service_method = getattr(service, cls.gam_method_name)
        logging.info(f"Method to be called:- {cls.gam_service_name }.{cls.gam_method_name}")

        offset = 0
        while True:
            cls.statement = (
                    cls.build_gam_lt_service_api_statement()
                    .Limit(cls.gam_pagination_limit)
                    .Offset(offset)
                )
            statement_query = cls.statement.ToStatement()
            logging.info(f'Statement Query: {statement_query}')
            response = service_method(statement_query)
            response = zeep.helpers.serialize_object(response)
            if result := response.get('results'):

                records = []
                for record in result:
                    try:
                        records.append(cls.gam_lt_input_model(**record).model_dump())
                    except Exception as e:
                        logging.info(f"record for which failed: {record}")
                        logging.info(f"{type(e).__name__}: {e}")
                logging.info(f"Records length:- {len(records)}")
                logging.info(records[:2])
                yield records
                offset += cls.gam_pagination_limit
                cls.statement.Offset(offset)
                cls.gam_batch += 1

            else:
                logging.info(f"No more {cls.__name__} to fetch.")
                cls.gam_batch = 0
                break
        logging.info(f"Fetching from {cls.__name__} complete")

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def fetch_via_report(cls, gam_client,start_date: date, end_date: date, spark: pyspark.sql.SparkSession,  *args, **kwargs):

        logging.info(f"Start fetching from GAM API for {cls.__name__} Report.")

        reportFilePath = os.path.join(cls.JobConfigs.CHANNEL['reportLocalDownloadFilePath'], cls.__name__, cls.trigger_date.strftime("%Y%m%d"))

        logging.info(f"reportFilePath: {reportFilePath}")
        import copy
        cls.statement: ad_manager.StatementBuilder = (
            cls.build_gam_lt_report_api_statement()
            .Limit(None)
            .Offset(None)
        )

        cls.report_job = {
            'reportQuery': {
                'dimensions': cls.JobConfigs.CHANNEL["entities"][cls.__name__]["report"]["dimensions"],
                'columns': cls.JobConfigs.CHANNEL["entities"][cls.__name__]["report"]["columns"],
                'adUnitView': 'HIERARCHICAL',
                'statement': cls.statement.ToStatement(),
                'dateRangeType': 'CUSTOM_DATE',
                'startDate' : start_date,
                'endDate' : end_date
            }
        }

        logging.info(f"Report Job: {cls.report_job}")
        report_downloader = gam_client.GetDataDownloader(version=cls.JobConfigs.GAM_VERSION)
        report_job_id = report_downloader.WaitForReport(cls.report_job)
        logging.info(f"{cls.__name__} Report generated.")
        logging.info(f"{cls.__name__} Report Job ID is: {report_job_id}")

        if not os.path.exists(reportFilePath): os.makedirs(reportFilePath)

        with tempfile.NamedTemporaryFile(
            dir=reportFilePath, 
            suffix='.csv.gz', 
            delete=False
            ) as report_file:
            logging.info(f"Report File Path is: {reportFilePath}")
            report_downloader.DownloadReportToFile(
                report_job_id=report_job_id,
                export_format='CSV',
                outfile=report_file,
                use_gzip_compression=True
            )
            logging.info(f"Report name for {cls.__name__} Report: {report_file.name}")

        logging.info(f"downloading the  report to : {reportFilePath}")

        report_df: pyspark.sql.DataFrame = (
            spark.read
            .format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(reportFilePath)
        )

        lt_col_map = cls.JobConfigs.CHANNEL["ltRenameMap"]["report"]
        for col in report_df.columns:
            if col in lt_col_map.keys():
                report_df = report_df.withColumnRenamed(col, lt_col_map[col])

        logging.info("report generated:-")
        report_df.show()

        return report_df

    @classmethod
    def fetch_via_service(cls, gam_client: ad_manager.AdManagerClient, spark: pyspark.sql.SparkSession):
        service_df = None
        for gam_records in cls.fetch_service(gam_client=gam_client):
            logging.info("GAM records fetched:-")

            if len(gam_records) > 0:
                df_batch = spark.createDataFrame(gam_records,schema=cls.gam_service_input_lt_sync_schema())

                logging.info("New records from GAM:-")
                df_batch.show(10)
                service_df = service_df.unionByName(df_batch, allowMissingColumns=True) if service_df else df_batch

        entity_name_str = cls.gam_entity.lower()
        lt_col_map = cls.JobConfigs.CHANNEL["ltRenameMap"]["service"]

        for col in service_df.columns:
            if col == 'id':
                service_df = service_df.withColumnRenamed('id', f"{entity_name_str}_id")
            if col == 'name':
                service_df = service_df.withColumnRenamed('name', f"{entity_name_str}_name")
            if col in lt_col_map.keys():
                service_df = service_df.withColumnRenamed(col, lt_col_map[col])

        return service_df

    @classmethod
    def merge_service_report_metrics(cls, service_df: pyspark.sql.DataFrame, report_df: pyspark.sql.DataFrame):
        logging.info("Starting to merge the 2 Dataframes.")
        service_df = service_df.select(*[F.col(c).alias(f"service_{c}") for c in service_df.columns])
        service_df.show()
        report_df = report_df.select(*[F.col(c).alias(f"report_{c}") for c in report_df.columns])
        report_df.show()
        entity_name_str = cls.gam_entity.lower()

        merged_df: pyspark.sql.DataFrame = service_df.join(
            other=report_df,
            on=(F.col(f"service_{entity_name_str}_id")==F.col(f"report_{entity_name_str}_id")),
            how="left"
        )
        merged_df.printSchema()

        merged_df = (
            merged_df
            .withColumn(
                f"service_{entity_name_str}_start_date",
                F.col("service_startDateTime")
            )
            .withColumn(
                f"service_{entity_name_str}_end_date",
                F.when(
                    F.col("service_unlimitedEndDateTime") == True,
                    F.to_date(F.lit("9999-12-31"))
                ).otherwise(F.col("service_endDateTime"))
            )
            .withColumn(
                f"service_report_start_date",
                F.col(f"service_{entity_name_str}_start_date")
            )
            .withColumn(
                "service_report_end_date",
                F.when(
                    F.col(f"service_{entity_name_str}_end_date") < F.lit(cls.trigger_date),
                    F.col(f"service_{entity_name_str}_end_date")
                ).otherwise(F.lit(cls.trigger_date))
            ).withColumn(
                "is_active",
                F.when(
                    F.col(f"service_{entity_name_str}_end_date") > F.lit(cls.trigger_date),
                    F.lit(1)
                ).otherwise(F.lit(0))
            )
        )

        for col_name in cls.JobConfigs.CHANNEL["entities"][cls.__name__]['final']['columns']:

            service_col = f"service_{col_name}"
            report_col = f"report_{col_name}"
            if service_col in merged_df.columns:
                merged_df = merged_df.withColumnRenamed(service_col, col_name)

            elif report_col in merged_df.columns:
                merged_df = merged_df.withColumnRenamed(report_col, col_name)

            logging.info(f"Cols: {col_name}")

        merged_df = merged_df.withColumn("data_refresh_date", F.to_date(F.lit(cls.trigger_date), "yyyy-MM-dd"))

        merged_df = merged_df.select(*cls.JobConfigs.CHANNEL["entities"][cls.__name__]['final']['columns'])
        merged_df.show()
        logging.info("Merging Complete.")
        return merged_df

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def push_lt_report(cls, storage_conns, dataframe=None):
        logging.info("Uploading the files to storage:-")
        if dataframe is None:
            logging.error("No dataframe provided to push_lt_report.")
            raise ValueError("Dataframe cannot be None.")
        
        if isinstance(dataframe, pyspark.sql.DataFrame):
            dataframe = dataframe.toPandas()

        trigger_date_str = cls.trigger_date.strftime("%Y%m%d")
        file_name = f"{cls.JobConfigs.CHANNEL['entities'][cls.__name__]['gcsFileName']}_{trigger_date_str}.csv.gz"
        source = os.path.join(cls.JobConfigs.CHANNEL["localDownloadFilePath"], file_name)
        destination = os.path.join(cls.JobConfigs.CHANNEL["gcsBaseFilepath"], file_name)
        logging.info(f"Source: {source}")
        logging.info(f"Destination: {destination}")
        dataframe.to_csv(source, index=False, compression='gzip', encoding='utf-8')
        for storage_conn in storage_conns:
            storage_conn.upload_file(source=source, destination=destination, content_type="application/octet-stream")
            logging.info(f"Uploaded to Storage {storage_conn.bucket_name}: {destination}")
        logging.info(f"Dataframe written to local path: {source}")
        return destination

    @classmethod
    def lt_sync(cls, gam_client, spark: pyspark.sql.SparkSession, gcs_storage_conns=[], *args, **kwargs):
        """Generic sync if no custom sync provided in the child class.
        Args::
            mongo_client: 
            gam_client: 
            synched_entities: List of entities already synched.

        Note:: Triggers the flow as follows :- 
            -> Fetch from GAM as per the statement.
            -> Massage data as per the model.
            -> Write to respective mongo coll. of the Child class.
        """
        logging.info(f"Start LT Sync for {cls.__name__}")
        cls.init_lt_class()
        sync_status = False
        error_message = ''

        try:
            service_df = cls.fetch_via_service(
                gam_client=gam_client, 
                spark=spark
                )

            report_df = cls.fetch_via_report( 
                gam_client=gam_client, spark=spark,  
                start_date=cls.earliest_date_acceptable, 
                end_date=cls.latest_date_acceptable
                )

            final_df: pyspark.sql.DataFrame = cls.merge_service_report_metrics(
                report_df=report_df, 
                service_df=service_df
                ).cache()

            final_df: pyspark.sql.DataFrame = cls.post_entity_lt_processing(spark ,final_df, gcs_storage_conns).cache()

            logging.info(f"Audit Dataframe len : {final_df.count()}")
            report_destination = cls.push_lt_report( dataframe=final_df, storage_conns=gcs_storage_conns)

            sync_status = True
            isSuccess=True
            report_status_message = f"Sync Successful. New data generated at :- {report_destination}"
            logging.info(report_status_message)

        except Exception as e:

            logging.error(f"Failed during the sync of {cls.__name__}")
            error_message = f"{type(e).__name__}: {e}"
            logging.error(error_message)
            sync_status = False
            isSuccess=False
            report_status_message = f"{type(e).__name__}:{e}"
            logging.error(report_status_message)

        finally:
            logging.info(f"End LT Sync for {cls.__name__}")

            report = cls.generate_job_report(
                start_date=cls.earliest_date_acceptable,
                end_date=cls.latest_date_acceptable,
                trigger_date=cls.trigger_date,
                isSuccess=isSuccess,
                operation_name="lt_sync_report_gen",
                message=report_status_message
            )

            cls.upload_job_status_report(
                storage_conns=gcs_storage_conns,
                report=report
            )

            return sync_status