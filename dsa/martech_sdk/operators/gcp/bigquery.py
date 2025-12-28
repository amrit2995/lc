import sys
from martech_sdk.utils import logging
from martech_sdk.operators import BaseOperator
from google.cloud import bigquery

class ReturnType:
    PANDAS_DF = 'pandas_df'
    SPARK_DF = 'spark_df'
    BIGQUERY_RESULT = 'bigquery_result'


class ReturnType:
    PANDAS_DF = 'pandas_df'
    SPARK_DF = 'spark_df'
    BIGQUERY_RESULT = 'bigquery_result'


class BigQueryOperator(BaseOperator):

    def __init__(self) -> None:
        super().__init__()
        self.bq_client = None
    
    def get_client(self) -> bigquery.Client:
        if not self.bq_client:
            self.bq_client = bigquery.Client()
            logging.info('Creating BQ client created.')
        return self.bq_client

    def execute(self, query: str):

        logging.info(f"Executing query:- {query}")
        result = self.get_client().query(query).result()
        logging.info("Query executed successfully..")
        return result
    
    @staticmethod
    def truncate_table(client, table_ref=''):
        logging.info('Delete all old BQ records')

        if not table_ref:
            table_ref = f"{project_id}.{dataset_id}.{table_id}"

        try:
            client.delete_table(table_ref)
            logging.info(f"Table {table_ref} deleted successfully.")
        except Exception as e:
            logging.info(f"Failed to delete table {table_ref}: {e}")

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
            df_batch = BigQueryOperator.read_batch(client=client, query=query, batch_size=batch_size, offset=offset)
            if df_batch.empty:
                break
            yield df_batch
            offset += batch_size

    
