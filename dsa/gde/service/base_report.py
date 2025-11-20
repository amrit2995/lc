from delta_sdk.utils import logging
from googleads import ad_manager
from gam_daci_etl.configs import JobConfigs
# from gam_daci_etl.utils.job_report import JobReport
import os
import tempfile
from datetime import datetime, timedelta, date
import pytz
import pandas as pd
import sqlalchemy
import subprocess
from delta_sdk.utils.common import CommonUtils

class BaseReportEntity:

    @classmethod
    def init_class(cls):
        cls.JobConfigs = JobConfigs

        cls.statement: ad_manager.StatementBuilder = (
            ad_manager
            .StatementBuilder(version=cls.JobConfigs.GAM_VERSION)
            .Limit(None)
            .Offset(None)
            )
        
        cls.write_batch_size = 100000
        cls.configs = cls.JobConfigs.CHANNEL["entities"][cls.__name__]["report"]
        cls.read_query = None
        cls.gam_fetch_date_range = int(cls.JobConfigs.CHANNEL["gam_fetch_date_range"]) - 1

        if JobConfigs.TRIGGERED_DATE_STR:
            cls.trigger_date = datetime.strptime(JobConfigs.TRIGGERED_DATE_STR, "%Y-%m-%d").date()
        else:
            cls.trigger_date: date = datetime.now(tz=pytz.timezone(cls.JobConfigs.TIME_ZONE)).date()
        # cls.trigger_date: date = datetime(year=2025, month=3, day=18).date()
        cls.gam_report_end_date: date = cls.trigger_date - timedelta(1)
        cls.gam_report_start_date: date = cls.gam_report_end_date - timedelta(days=cls.gam_fetch_date_range+1)
        # cls.gam_report_start_date: date = cls.gam_report_end_date - timedelta(days=7)

    @classmethod
    def show_user(cls, gam_client):
        userService = gam_client.GetService('UserService', version=cls.JobConfigs.GAM_VERSION)
        currentUser = userService.getCurrentUser()
        return currentUser

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def fetch_report(cls, gam_client, report_date: str, *args, **kwargs) -> str:

        logging.info(f"Start fetching from GAM API for {cls.__name__} Report.")
        reportFilePath = os.path.join(cls.JobConfigs.CHANNEL['reportDownloadFilePath'], cls.__name__, report_date)

        cls.build_report_statement()

        cls.report_job = {
            'reportQuery': {
                'dimensions': cls.configs["gam"]["dimensions"],
                'columns': cls.configs["gam"]["columns"],
                'adUnitView': 'HIERARCHICAL',
                'statement': cls.statement.ToStatement(),
                'dateRangeType': 'CUSTOM_DATE',
                'startDate' : datetime.strptime(report_date, "%Y-%m-%d").date(),
                'endDate' : datetime.strptime(report_date, "%Y-%m-%d").date()
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
        return reportFilePath

    @classmethod
    def custom_process_report(cls, df, *args, **kwargs):
        """When no custom process is defined."""
        return df

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def read_report_files(cls, source_path: str) -> pd.DataFrame:
        files = [f for f in os.listdir(source_path) if f.endswith((".csv", ".csv.gz"))]
        files = max([os.path.join(source_path, f) for f in files ], key=os.path.getmtime).split('/')[-1]
        files = [files]

        df_list  = []
        for file in files:
            file_path = os.path.join(source_path, file)
            print(f"Reading {file_path}...")
            df_batch = pd.read_csv(file_path)
            logging.info("Skipping Total in last row.")

            if df_batch.iloc[-1].astype(str).str.contains('Total', case=False).any():
                df_batch = df_batch.iloc[:-1]

            df_list.append(df_batch)
        
        df = pd.concat(df_list, ignore_index=True)
        return df

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def process_report(cls, df: pd.DataFrame, *args, **kwargs)-> pd.DataFrame:

        logging.info(f"Input table cols :- {df.columns.tolist()}")

        df["Column.AD_SERVER_CTR"] = pd.to_numeric(df["Column.AD_SERVER_CTR"], errors='coerce')
        df["Column.AD_SERVER_CTR"] = (df["Column.AD_SERVER_CTR"] * 100).round(2)

        df = cls.custom_process_report(df)
        df = df.rename(columns=cls.JobConfigs.CHANNEL["reportRenameMap"])

        df['data_refresh_date'] = cls.trigger_date.strftime('%Y-%m-%d')
        df['report_date'] = pd.to_datetime(df['report_date']).dt.date
        df['data_refresh_date'] = pd.to_datetime(df['data_refresh_date']).dt.date

        logging.info(df.head())
        logging.info(f"Output table cols :- {df.columns.tolist()}")

        return df

    def read_from_pg(pg_conn, table_name, report_date):
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE report_date = DATE '{report_date}';
        """
        df = pd.read_sql(query, con=pg_conn)
        return df.reset_index(drop=True)

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def delete_from_pg(cls, pg_conn, table_name, report_date):
        logging.info(f"PG conn : ")        
        logging.info(pg_conn)
        query = f"""
            DELETE FROM {table_name}
            WHERE report_date = DATE '{report_date}'
        """
        logging.info(f"Delete Query: \n {query}")

        deleted_df = None
        with pg_conn.cursor() as cur:
            cur.execute(query)
            pg_conn.commit()
            logging.info("Deletion completed successfully.")
        del deleted_df

    @classmethod
    def drop_pg(cls , pg_conn, table_name):
        logging.info(f"Table Name: {table_name}")

        query = f"""
            drop table daci_processor.public.{table_name};
        """

        logging.info(f"Delete Query: \n {query}")

        with pg_conn.cursor() as cur:
            cur.execute(query)
            pg_conn.commit()


    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def already_ingested(cls, pg_conn, table_type):


        table_name = cls.configs["pg"][f"{table_type}TableId"]
        trigger_date = cls.trigger_date.strftime("%Y-%m-%d")

        logging.info(f"Table Type: {table_type}")
        logging.info(f"Table Name: {table_name}")

        # try:

        query = f"""
            SELECT data_refresh_date
            FROM {table_name}
            WHERE data_refresh_date >= DATE '{trigger_date}';
        """
        logging.info(f"Read query: {query}")
        with pg_conn.cursor() as cur:
            cur.execute(query)
            existing_records = cur.fetchall()
            logging.info(f"Data len: {len(existing_records)}")
            return bool(len(existing_records)> 0)
        return False

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def merge_old_new_df(cls, old_records_df: pd.DataFrame, new_records_df: pd.DataFrame) -> pd.DataFrame:

        # old_records_df: pd.DataFrame = cls.apply_schema(old_records_df)
        # new_records_df: pd.DataFrame = cls.apply_schema(new_records_df)

        new_records_df_cols = set(list(new_records_df.columns))
        new_records_df_cols  = set(new_records_df_cols).intersection()

        logging.info(f"Old df len : {len(old_records_df)}")
        logging.info(f"Old df cols : {old_records_df.dtypes}")
        logging.info(f"New df len : {len(new_records_df)}")
        logging.info(f"New df cols : {new_records_df.dtypes}")

        final_column_name = cls.configs["pg"]["final_main_columns"]
        columns_to_match = cls.configs["pg"]["columns_to_match"]
        columns_to_update = cls.configs["pg"]["columns_to_update"]
        overwrite = cls.JobConfigs.CHANNEL["overwrite_data_in_main"]
        duplicate_cols = list(set(final_column_name) - set(columns_to_match) - set(columns_to_update) - set(['discrepancy_fields', 'discrepancy_found']))

        logging.info("Merging BQ and new GAM records")
        merged_df = pd.DataFrame()
        if old_records_df.empty:
            logging.info("BQ records DF is empty , Passing New GAM records")
            new_records_df["discrepancy_found"] = 0
            new_records_df["discrepancy_fields"] = ""
            merged_df = new_records_df[final_column_name]
            return merged_df

        logging.info('Applying schema to make datatype of both the dataframes uniform')

        logging.info("Merging the max values from old and new data for the existing records as well as appending the new values.")
        merged_df = pd.merge(old_records_df, new_records_df, how='outer', on=columns_to_match, suffixes=('_old', '_new'))

        def update_columns(row, overwrite, compare_cols, duplicate_cols):

            for col in duplicate_cols:
                row[col] = row[f"{col}_new"]

            discrepancy_cols = []

            for col in compare_cols:
                try:

                    val_new = row[f"{col}_new"]
                    val_old = row[f"{col}_old"]

                    if col in ("impressions", "clicks"):
                        val_new = int(val_new)
                        val_old = int(val_old)

                    if val_new < val_old:
                        if overwrite: 
                            row[col] = val_new
                        else: 
                            row[col] = val_old
                        discrepancy_cols.append(col)
                    else:
                        row[col] = val_new
                except Exception as e:
                    logging.error(f"{type(e).__name__}:{e}")
                    logging.error(f"row: {row}")
                    logging.error(f"col: {col}")
                    logging.error(f"{val_new}: {type(val_new)}")
                    logging.error(f"{val_old}: {type(val_old)}")

            row["discrepancy_found"] = int(bool(len(discrepancy_cols) > 0))
            row["discrepancy_fields"] = ",".join(discrepancy_cols)
            return row
        
        merged_df = merged_df.apply(lambda row: update_columns(row, overwrite, compare_cols=columns_to_update, duplicate_cols=duplicate_cols), axis=1)
        merged_df = merged_df[final_column_name]
        logging.info(f"Merged_df:")
        logging.info(merged_df.head())
        return merged_df


    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def push_report(cls , report_date: str, table_type: str, storage_conns, pg_conn=None, dataframe: pd.DataFrame=None):

        trigger_date_str = cls.trigger_date.strftime("%Y%m%d")
        file_name =  f"{cls.configs['pg'][f'{table_type}TableId']}_{report_date}.csv.gz"
        source = os.path.join(cls.JobConfigs.CHANNEL["localBaseFilePath"], file_name)
        destination = os.path.join(cls.JobConfigs.CHANNEL["gcsBaseFilepath"], trigger_date_str, file_name)

        dataframe.to_csv(source, index=False, compression='gzip', encoding='utf-8')
        # dataframe.to_parquet(source, index=False, compression='snappy', engine='pyarrow')
        for storage_conn in storage_conns:
            storage_conn.upload_file(source=source, destination=destination, content_type="application/octet-stream")
            logging.info(f"Uploaded to Storage {storage_conn.bucket_name}: {destination}")
        # del dataframe
        # logging.info('Del df for push report')

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def job_report(cls, pg_conn, is_report_success, message=''):
        table_name = JobConfigs.CHANNEL["job_status_report_table_name"]

        record = {
                "startDate": cls.gam_report_start_date,
                "endDate": cls.gam_report_end_date,
                "jobRunDate": cls.trigger_date,
                "reportingType": cls.__name__,
                "isReportSuccess": int(bool(is_report_success)),
                "message": message
            }
        df = pd.DataFrame([record])

        pg_engine = sqlalchemy.create_engine("postgresql+psycopg2://", creator=lambda: pg_conn)
        df.to_sql(table_name, pg_engine, if_exists="append", index=False)
        logging.info(f"Status : {record}")

    @classmethod
    def clear_gc(cls):
        import psutil
        import gc
        process = psutil.Process(os.getpid())
        logging.info("Before GC")
        memory_usage_after_gc = process.memory_info().rss / (1024 * 1024)
        logging.info(f"Memory before GC: {memory_usage_after_gc:.2f} MB")
        gc.collect()
        logging.info("Cleared GC")
        memory_usage_after_gc = process.memory_info().rss / (1024 * 1024)
        logging.info(f"Memory After GC: {memory_usage_after_gc:.2f} MB")


    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def delete_reports_from_local(cls, path):
        subprocess.run(['rm', '-rf', path])
        logging.info(f"Deleted files successfully from : {path}")


    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def daywise_report_sync(cls, report_date: str, gam_client, pg_conn=None, gcs_storage_conns=[], *args, **kwargs):

        report_file_path = cls.fetch_report(gam_client, report_date=report_date)
        new_gam_records_df = cls.read_report_files(source_path=report_file_path)
        new_gam_records_df = cls.process_report(df=new_gam_records_df)

        final_column_name = cls.configs["pg"]["final_audit_columns"]
        table_name=cls.configs["pg"]["auditTableId"]
        logging.info(f"Entity Name: {cls.__name__} Table Type: audit \n Trigger Date: {cls.trigger_date.strftime('%Y-%m-%d')} \n Report Date: {report_date} \n Table Name: {table_name} \n Column Names: {final_column_name} ")
        final_audit_df = new_gam_records_df[final_column_name]
        logging.info(f"Audit Dataframe len : {len(final_audit_df)}")
        # cls.write_2_pg(dataframe=final_audit_df, table_name=table_name, pg_conn=pg_conn)
        cls.push_report( dataframe=final_audit_df, report_date=report_date, table_type="audit", storage_conns=gcs_storage_conns)

        df_lists = ['final_main_df', 'final_audit_df', 'old_records_df', 'new_gam_records_df']
        for df in df_lists:
            logging.info(f"Deleting {df} df")
            if df in globals():
                del globals()[df]

            if df in locals():
                del locals()[df]

        cls.clear_gc()

    @classmethod
    @CommonUtils.execution_time_calc_decorator
    def report_sync(cls, gam_client, pg_conn=None, gcs_storage_conns=None, *args, **kwargs):
        is_report_success = False
        report_status_message = ''
        try:
            cls.init_class()
            # already_ingested_audit, already_ingested_main = cls.already_ingested(pg_conn, "audit"), cls.already_ingested(pg_conn, "main")
            
            date_range = int(cls.JobConfigs.CHANNEL["gam_fetch_date_range"])
            report_date_list = [ (cls.trigger_date - timedelta(delta)).strftime("%Y-%m-%d") for delta in range(date_range, 0, -1)]
            logging.info(f"Report Date list: {report_date_list}")
            for report_date in report_date_list:
                cls.daywise_report_sync(report_date=report_date, gam_client=gam_client, pg_conn=pg_conn, gcs_storage_conns=gcs_storage_conns)


        except Exception as e:
            print("Error in report sync", e)
            logging.error(f"Job Failed for {cls.__name__} Report.")
            report_status_message = f"{type(e).__name__}:{e}"
            logging.error(report_status_message)
            
        finally:

            report = cls.generate_job_report(
                start_date=cls.gam_report_start_date,
                end_date=cls.gam_report_end_date,
                trigger_date=cls.trigger_date,
                isSuccess=is_report_success,
                operation_name="lt_sync_report_gen",
                message=report_status_message
            )
            cls.upload_job_status_report(
                storage_conns=gcs_storage_conns,
                report=report
            )
 
            logging.info(f"End Sync for {cls.__name__}")