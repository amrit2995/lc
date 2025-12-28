from delta_sdk.configs.connConfigs import GCS
from google.cloud import bigquery
from delta_sdk.connectors.base import BaseConnector
from delta_sdk.utils import logging
import asyncio
import sys
import pandas as pd
import pyspark
from delta_sdk.utils.spark import SparkUtils
from delta_sdk.utils.common import CommonUtils

class BQWriteMode:
    OVERWRITE = 'overwrite'
    APPEND = 'append'

    @classmethod
    def list_modes(cls):
        return [cls.OVERWRITE, cls.APPEND]

class GCSBigQueryConnector(BaseConnector):
    def __init__(self, 
                env: str,
                nucleusHash: str ='',
                base_path: str='',
                region: str='east'):

        super().__init__(env=env, applicationName=GCS["bq"]["applicationName"][env], scope=GCS["bq"]["scope"][env],
                          nucleusHash=nucleusHash, base_path=base_path, region=region)
        self._client = None
        self.gcp = True

    @property
    @CommonUtils.retry_connection(max_retries=2, delay=1)
    def client(self):
        if not self._client:
            try:
                credentials = self.get_gcs_creds()
                self._client = bigquery.Client(credentials=credentials)
            except Exception as e:
                logging.error(f"Client Creation failed : {e}")
        return self._client

class GCSBigQueryOperators:

    @staticmethod
    def row_count(client, project_id, dataset_id, table_id):
        query = f"""
        SELECT COUNT(*) as row_count
        FROM `{project_id}.{dataset_id}.{table_id}`
        """
        query_job = client.query(query)
        results = query_job.result()
        row_count = next(results).row_count
        logging.info(f"Row count: {row_count}")
        return row_count

    @staticmethod
    def read_batch(client, query, batch_size,offset):
        paginated_query = f"{query} LIMIT {batch_size} OFFSET {offset};"
        logging.info("Paginated Query:")
        logging.info(paginated_query)
        query_job = client.query(paginated_query)
        df_batch = query_job.to_dataframe()
        logging.info(df_batch.head(5))
        return df_batch

    @staticmethod
    def read_in_batch_gen(client, query, batch_size=1000, offset=0, limit=sys.maxsize):
        while offset <= limit:
            df_batch = GCSBigQueryOperators.read_batch(client=client, query=query, batch_size=batch_size, offset=offset)
            if df_batch.empty:
                break
            yield df_batch
            offset += batch_size

    @staticmethod
    def truncate_table(client, project_id='', dataset_id='', table_id='', table_ref=''):
        logging.info('Delete all old BQ records')

        if not table_ref:
            table_ref = f"{project_id}.{dataset_id}.{table_id}"

        try:
            client.delete_table(table_ref)
            logging.info(f"Table {table_ref} deleted successfully.")
        except Exception as e:
            logging.info(f"Failed to delete table {table_ref}: {e}")

    @staticmethod
    def write_batch(client, dataframe, start, end, batch_size, project_id, dataset_id, table_id):
        batch = dataframe.iloc[start:end]
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        batch_status = {}
        try:
            job = client.load_table_from_dataframe(batch, table_ref)
            job.result()
            batch_status = {
                "batch_number": start // batch_size + 1,
                "batch_start": start,
                "batch_end": end - 1,
                "status": "success", 
                "rows": len(batch)
                }
        except Exception as e:
            batch_status = {
                "batch_number": start // batch_size + 1,
                "batch_start": start,
                "batch_end": end - 1,
                "status": "failed", 
                "rows": len(batch), 
                "error": str(e)
                }
        finally: 
            logging.info(batch_status)
            return batch_status

    @staticmethod
    def write_in_batch_gen(client, dataframe, project_id, dataset_id, table_id, batch_size=10000, write_mode=BQWriteMode.APPEND):

        if write_mode == BQWriteMode.OVERWRITE:
            GCSBigQueryOperators.truncate_table(client=client, project_id=project_id, dataset_id=dataset_id, table_id=table_id)

        total_rows = len(dataframe)
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            yield GCSBigQueryOperators.write_batch(client, dataframe, start, end, batch_size, project_id, dataset_id, table_id)


class AsyncGCSBigQueryOperators:

    @staticmethod
    async def read_batch(client, query, batch_size,offset):
        paginated_query = f"{query} LIMIT {batch_size} OFFSET {offset};"
        logging.info("Paginated Query:")
        logging.info(paginated_query)
        query_job = client.query(paginated_query)
        df_batch = query_job.to_dataframe()
        logging.info(df_batch.head(5))
        return df_batch

    # @staticmethod
    # async def _batch_reader(client, query, project_id, dataset_id, table_id, batch_size=1000, tps=5, offset=0, limit=sys.maxsize):
    #     tasks = []

    #     interval = 1/tps
    #     row_count = GCSBigQueryOperators.row_count(client=client, project_id=project_id, dataset_id=dataset_id, table_id=table_id)
    #     while True:
            
    #         if offset <= min(limit, row_count):
    #             # task = asyncio.create_task(AsyncGCSBigQueryOperators.read_batch(client=client, query=query, batch_size=batch_size, offset=offset))
    #             task = asyncio.to_thread(
    #                 GCSBigQueryOperators.read_batch,
    #                 client=client, query=query, batch_size=batch_size, offset=offset
    #                 )
    #             tasks.append(task)
    #             offset += batch_size
            
    #         completed_tasks = [task for task in tasks if task.done()]
    #         for completed in completed_tasks:
    #             tasks.remove(completed)
    #             yield completed.result()

    #         await asyncio.sleep(interval)

    @staticmethod
    async def _async_batch_reader_gen(client, query, project_id, dataset_id, table_id, batch_size=1000, tps=5, offset=0, limit=sys.maxsize):
        tasks = []
        interval = 1/tps
        row_count = GCSBigQueryOperators.row_count(client=client, project_id=project_id, dataset_id=dataset_id, table_id=table_id)
        while offset <= min(limit, row_count) or tasks:
            
            if offset <= min(limit, row_count):
                # task = asyncio.create_task(AsyncGCSBigQueryOperators.read_batch(client=client, query=query, batch_size=batch_size, offset=offset))
                logging.info(f"Fetching from {offset} to {offset+batch_size}")

                task = asyncio.to_thread(
                    GCSBigQueryOperators.read_batch,
                    client=client, query=query, batch_size=batch_size, offset=offset
                    )
                tasks.append(task)
                offset += batch_size
            
            completed_tasks = [task for task in tasks if task.done()]
            for completed in completed_tasks:
                tasks.remove(completed)
                yield await completed

            await asyncio.sleep(interval)


    @staticmethod
    def batch_reader_gen_sync(client, query, project_id, dataset_id, table_id, batch_size=1000, tps=5, offset=0, limit=sys.maxsize):
        async_gen = AsyncGCSBigQueryOperators._async_batch_reader_gen(
            client, query, project_id, dataset_id, table_id, batch_size=batch_size, tps=tps, offset=offset, limit=limit
        )
        loop = asyncio.get_event_loop()
        while True:
            try:
                yield loop.run_until_complete(async_gen.__anext__())
            except StopAsyncIteration:
                break

    @staticmethod
    async def batch_writer(client, dataframe, project_id, dataset_id, table_id, batch_size=10000, write_mode=BQWriteMode.APPEND, concurrent_batches=20):
        logging.info('Start writing in bathces.')
        if write_mode == BQWriteMode.OVERWRITE:
            GCSBigQueryOperators.truncate_table(client=client, project_id=project_id, dataset_id=dataset_id, table_id=table_id)
        
        total_rows = len(dataframe)

        tasks = []
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            task = asyncio.to_thread(
                GCSBigQueryOperators.write_batch, 
                client, dataframe, start, end, batch_size, project_id, dataset_id, table_id
                )
            tasks.append(task)

            if len(tasks)%concurrent_batches == 0 or end == total_rows:                
                results = await asyncio.gather(*tasks)
                logging.info(results)
                tasks = []

    @staticmethod
    async def batch_writer_semaphore(client, dataframe, project_id, dataset_id, table_id, batch_size=10000, write_mode=BQWriteMode.APPEND, concurrent_batches=20):
        logging.info('Start writing in bathces with semaphore.')
        if write_mode == BQWriteMode.OVERWRITE:
            GCSBigQueryOperators.truncate_table(client=client, project_id=project_id, dataset_id=dataset_id, table_id=table_id)

        semaphore = asyncio.Semaphore(concurrent_batches)
        total_rows = len(dataframe)

        async def semaphore_task(start, end):
            async with semaphore:
                await asyncio.to_thread(
                    GCSBigQueryOperators.write_batch,
                    client=client, dataframe=dataframe, start=start, end=end, batch_size=batch_size, project_id=project_id, dataset_id=dataset_id, table_id=table_id
                )

        tasks = []
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            tasks.append(semaphore_task(start, end))

        results = await asyncio.gather(*tasks)
        logging.info(results)

    @staticmethod
    def write_in_batches_semaphore(client, dataframe: pd.DataFrame, project_id, dataset_id, table_id, write_mode=BQWriteMode.APPEND, concurrent_batches=20, batch_size=10000):
        asyncio.run(AsyncGCSBigQueryOperators.batch_writer_semaphore(client, dataframe, project_id, dataset_id, table_id, batch_size=batch_size, write_mode=write_mode, concurrent_batches=concurrent_batches))

    @staticmethod
    def write_in_batches(client, dataframe: pd.DataFrame, project_id, dataset_id, table_id, write_mode=BQWriteMode.APPEND, concurrent_batches=20, batch_size=10000):
        asyncio.run(AsyncGCSBigQueryOperators.batch_writer(client, dataframe, project_id, dataset_id, table_id, batch_size=batch_size, write_mode=write_mode, concurrent_batches=concurrent_batches))

class SparkGCSBigQueryOperators:

    @staticmethod
    def reader(project_id, dataset_id, table_id, spark: pyspark.sql.SparkSession=None):

        if not spark:
            spark = SparkUtils.get_default_spark_builder().getOrCreate()

        spark_reader = (
            spark.read
            .format("bigquery")
            .option('project', project_id)
            .option("dataset", dataset_id)
            .option("table", table_id)
        )

        logging.info(f'Returning spark reader object. Exceute by <reader_object>.load() to trigger.')
        return spark_reader

    @staticmethod
    def writer(dataframe: pyspark.sql.dataframe.DataFrame, env, project_id, dataset_id, table_id, write_mode=BQWriteMode.APPEND):
        spark_writer = (
            dataframe.write
            .format("bigquery")
            .option("project", project_id)
            .option("dataset", dataset_id)
            .option("table", table_id)
            .option("temporaryGcsBucket", GCS['storage']['bucketName'][env])
            .mode(write_mode)
        )

        logging.info(f'Returning spark writer object. Exceute by <writer_object>.save() to trigger.')

        return spark_writer
