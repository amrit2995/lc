import pyspark.sql
import sys
from delta_sdk.connectors.base import BaseConnector
import psycopg2
import pyspark
from sqlalchemy import create_engine
import sqlalchemy
from delta_sdk.configs.connConfigs import POSTGRES
from delta_sdk.utils import logging
import pandas as pd
import asyncio
import json
from delta_sdk.utils.spark import SparkUtils
from delta_sdk.utils.common import CommonUtils, BatchExec
    
class PostgresWriteMode:
    OVERWRITE = 'overwrite'
    APPEND = 'append'

    @classmethod
    def list_modes(cls):
        return [cls.OVERWRITE, cls.APPEND]
    
class PostgresMode:
    READ = 'r'
    READ_AND_WRITE = 'rw'

class PostgresCreds:
    def __init__(self, port, user, url=None, host=None, code=None, ca=None, cert=None, key=None):
        self.urls = url
        self.hosts = host
        self.port = port
        self.user = user
        self.code = code
        self.ca = ca
        self.cert = cert
        self.key = key

        if not self.hosts:
            self.hosts = self.urls
    
    def __call__(self, key=None):
        if hasattr(self, key):
            return getattr(self, key)
        return {'url': self.urls, 'host': self.hosts, 'port': self.port, 'user': self.user, 'password': self.code}

    def __repr__(self):
        return f"PostgresCreds(host={self.hosts}, url={self.urls}, port={self.port}, user={self.user}, code=****)"

class PostgresConnector(BaseConnector):
    def __init__(self, 
                env: str = '',
                clusterName: str ='onprem',
                nucleusHash: str ='',
                base_path: str='',
                region: str='east'
                ):

        super().__init__(env=env, applicationName=POSTGRES["applicationName"][env], scope=POSTGRES["scope"][clusterName],
                          nucleusHash=nucleusHash, base_path=base_path, region=region)

        self.mode = 0
        self.clusterName = clusterName
        self.dbname = None
        self._connection = None
        self._pg_creds = None
    

    @CommonUtils.retry_connection(max_retries=2, delay=1)
    def _get_connection(self, pg_creds: PostgresCreds):

        sslrootcert = self._createCredsFile(data=pg_creds.ca, file_name="root.crt")
        sslcert = self._createCredsFile(data=pg_creds.cert, file_name="server.crt")
        sslkey = self._createCredsFile(data=pg_creds.key, file_name="server.key", permission_code="600")

        pg_conn = psycopg2.connect(
                host=pg_creds.hosts,
                port=pg_creds.port,
                user=pg_creds.user,
                password=pg_creds.code,
                dbname=self.dbname,
                sslmode="verify-full",
                sslrootcert=sslrootcert,
                sslcert=sslcert,
                sslkey=sslkey
            )
        return pg_conn

    def is_replica(self, pg_conn: psycopg2.extensions.connection):
        is_replica = False
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute("SELECT pg_is_in_recovery();")
                pg_data = cursor.fetchone()[0]
                is_replica = True if pg_data else False
                if is_replica:
                    logging.info("This is a REPLICA. Only read is possible vis this")
                else:
                    logging.info("This is the MASTER.")
        except Exception as e:
            logging.error(f"{type(e).__name__}: {e}")
        finally:
            return is_replica


    def get_connection(self, dbname, mode: str=PostgresMode.READ):

        create_new = False
        if not self._connection:
            create_new = True

        if not self.dbname or self.dbname != dbname:
            self.dbname = dbname
            create_new = True

        if create_new:
            pg_creds: PostgresCreds=self.get_postgres_creds()
            if mode == PostgresMode.READ_AND_WRITE:
                hosts_list = pg_creds.hosts.split(',')
                
                for host in hosts_list:
                    pg_creds.hosts = host
                    logging.info(f"Trying connection with host:- {pg_creds.hosts}")
                    pg_conn = self._get_connection(pg_creds=pg_creds)
                    if not self.is_replica(pg_conn=pg_conn):
                        self._connection = pg_conn
                        break
            else:
                self._connection = self._get_connection(pg_creds=pg_creds)
        
        return self._connection

    @CommonUtils.retry_connection(max_retries=1, delay=1)
    def get_engine(self, dbname, mode: str=PostgresMode.READ):
        pg_conn = self.get_connection(dbname=dbname, mode=mode)
        engine = sqlalchemy.create_engine("postgresql+psycopg2://", creator=lambda: pg_conn)
        return engine

    def get_postgres_creds(self) -> PostgresCreds:

        if not self._pg_creds:
            data = self.get_creds()

            if self.clusterName == 'onprem':
                urls = data["DB_URL"]
                data["host"] = ','.join([ f"{url}.lowes.com" for url in (urls).split(',')])

            self._pg_creds = PostgresCreds(
                url=self._get_value(data, ["db_url", "url", "host"]),
                host=self._get_value(data, ["host"]),
                port=self._get_value(data, ["db_port", "port"]),
                user=self._get_value(data, ["db_user", "user", "username"]),
                code=self._get_value(data, ["db_password", "password", "pwd"]),
                ca=self._get_value(data, ["ca"]),
                cert=self._get_value(data, ["key", "cert"]),
                key=self._get_value(data, ["client_key", "private_key"])
    )

        return self._pg_creds
        
    def get_jdbc_url(self,dbname):
        pg_creds = self.get_postgres_creds()
        jdbc_url = f"jdbc:postgresql://{pg_creds.hosts}:{pg_creds.port}/{dbname}?sslmode=require"
        logging.info(f"jdbc_url: {jdbc_url}")
        return jdbc_url

    def get_jdbc_properties(self):
        pg_creds = self.get_postgres_creds()
        jdbc_properties = { "user": pg_creds.user, "password": pg_creds.code, "driver": "org.postgresql.Driver"}
        logging.info(f"jdbc_properties: {jdbc_properties}")
        return jdbc_properties


class PostgresOperators:

    @staticmethod
    def read_batch_gen(conn: psycopg2.extensions.connection, query, batch_size=sys.maxsize):
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                while True:
                    records = cursor.fetchmany(batch_size)
                    if not records:
                        break
                    yield records
        except psycopg2.Error as e:
            logging.info(f"Database error occurred: {e}")
            raise

    @staticmethod
    def truncate_table(conn: psycopg2.extensions.connection, table_name):
        logging.info("Starting to truncating table")
        cursor = None
        logging.info(f"Conn: {conn}")
        try:
            with conn.cursor() as cursor:
                logging.info(f"cursor: {cursor}")
                truncate_sql = f"TRUNCATE TABLE {table_name} CASCADE;"
                cursor.execute(truncate_sql)
                conn.commit()
                logging.info(f"Table {table_name} has been truncated successfully.")

        except psycopg2.errors.UndefinedTable as e:
            logging.error(e)

    @staticmethod
    def write_in_batches(dataframe: pd.DataFrame, table_name, batch_size=sys.maxsize, write_mode=PostgresWriteMode.APPEND, engine: sqlalchemy.engine.base.Engine=None, *args, **kwargs):

        def write_to_db(df_batch: pd.DataFrame, engine, table_name, index=False):
            df_batch.to_sql(table_name, engine, if_exists='append', index=index)
        
        batch_exec = BatchExec(batch_size=batch_size)
        batch_exec.trigger_in_df_batches(func=write_to_db, dataframe=dataframe, table_name=table_name, engine=engine)

    @staticmethod
    def execute_batch_query(dataframe: pd.DataFrame, conn: psycopg2.extensions.connection, query, batchsize=sys.maxsize):
        
        def execute_query(df_batch, conn, query):
            records = [tuple(x) for x in df_batch.to_numpy()]
            with conn.cursor() as cur:
                psycopg2.extras.execute_values(cur, query, records)

        batch_exec = BatchExec(batch_size=batchsize)

        batch_exec.trigger_in_df_batches(func=execute_query, dataframe=dataframe, conn=conn, query=query)

class AsyncPostgresOperators:
    
    @staticmethod
    async def batch_writer_semaphore(dataframe: pd.DataFrame, dbname, table_name, batch_size=sys.maxsize, concurrent_batches=5, write_mode=PostgresWriteMode.APPEND, connection: psycopg2.extensions.connection=None, engine: sqlalchemy.engine.base.Engine=None, pg_sdk_connector: PostgresConnector=None):

        if write_mode == PostgresWriteMode.OVERWRITE:
            if pg_sdk_connector:
                connection = pg_sdk_connector.get_connection(dbname=dbname)
            PostgresOperators.truncate_table(conn=connection, table_name=table_name)

        if pg_sdk_connector:
            engine = pg_sdk_connector.get_engine(dbname=dbname)

        logging.info('Start concurrent writing in bathces with semaphore.')
        semaphore = asyncio.Semaphore(concurrent_batches)
        logging.info(f'Setting Semaphore limit to {concurrent_batches} | Semaphore {semaphore}')
        total_rows = len(dataframe)
        logging.info(f"Number of rows to be ingested: {total_rows}")
    
        async def semaphore_task(start, end):
            async with semaphore:
                await asyncio.to_thread(
            PostgresOperators.write_batch,
            engine=engine, dataframe=dataframe, start=start, end=end, table_name=table_name, batch_size=batch_size
            )

        tasks = []
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            tasks.append(semaphore_task(start, end))

        results = await asyncio.gather(*tasks)
        logging.info(results)

    @staticmethod
    async def batch_writer(dataframe: pd.DataFrame, dbname, table_name, batch_size=1000, concurrent_batches=5, write_mode=PostgresWriteMode.APPEND, connection: psycopg2.extensions.connection=None, engine: sqlalchemy.engine.base.Engine=None, pg_sdk_connector: PostgresConnector=None):

        if write_mode == PostgresWriteMode.OVERWRITE:
            if pg_sdk_connector:
                connection = pg_sdk_connector.get_connection(dbname=dbname)
            PostgresOperators.truncate_table(conn=connection, table_name=table_name)

        if pg_sdk_connector:
            engine = pg_sdk_connector.get_engine(dbname=dbname)

        total_rows = len(dataframe)
        logging.info(f"Number of rows to be ingested: {total_rows}")

        logging.info('Start concurrent writing in bathces')
        tasks = []
        for start in range(0, total_rows, batch_size):
            end = min(start + batch_size, total_rows)
            task = asyncio.to_thread(
                        PostgresOperators.write_batch,
                        engine=engine, dataframe=dataframe, start=start, end=end, table_name=table_name, batch_size=batch_size
                    )
            tasks.append(task)

            if len(tasks)%concurrent_batches == 0 or end == total_rows:                
                results = await asyncio.gather(*tasks)
                logging.info(results)
                tasks = []

    @staticmethod
    def write_in_batches(dataframe: pd.DataFrame, dbname, table_name, batch_size, concurrent_batches, write_mode, connection: psycopg2.extensions.connection=None, engine: sqlalchemy.engine.base.Engine=None, pg_sdk_connector: PostgresConnector=None):
        asyncio.run(
            AsyncPostgresOperators.batch_writer(
                dataframe=dataframe,
                dbname=dbname,
                table_name=table_name,
                batch_size=batch_size,
                concurrent_batches=concurrent_batches,
                connection=connection,
                engine=engine,
                pg_sdk_connector=pg_sdk_connector
            )
        )

    @staticmethod
    def write_in_batches_semaphore(dataframe: pd.DataFrame, dbname, table_name, batch_size, concurrent_batches, connection: psycopg2.extensions.connection=None, engine: sqlalchemy.engine.base.Engine=None, pg_sdk_connector: PostgresConnector=None):
        asyncio.run(
            AsyncPostgresOperators.batch_writer_semaphore(
                dataframe=dataframe,
                dbname=dbname,
                table_name=table_name,
                batch_size=batch_size,
                concurrent_batches=concurrent_batches,
                connection=connection,
                engine=engine,
                pg_sdk_connector=pg_sdk_connector
            )
        )

class SparkPostgresOperators:

    @staticmethod
    def jdbc_reader(pg_sdk_connector: PostgresConnector, dbname, query='', schema='public', table_name='', spark: pyspark.sql.SparkSession=None) -> pyspark.sql.DataFrameReader:

        pg_creds = None

        if pg_sdk_connector:
            logging.info('Fetching url and properties from pg_sdk_connector')
            pg_creds = pg_sdk_connector.get_postgres_creds()
            jdbc_url = f"jdbc:postgresql://{pg_creds.hosts}:{pg_creds.port}/{dbname}?sslmode=require"

        dbtable=''
        if query:
            dbtable=query
        elif schema and table_name:
            dbtable = f"{schema}.{table_name}"

        logging.info('Read from Spark JDBC')

        if not spark:
            spark = SparkUtils.get_default_spark_builder().getOrCreate()

        spark_reader = (
            spark.read
            .format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", dbtable)
            .option("user", pg_creds.user)
            .option("password", pg_creds.code)
            .option("driver", "org.postgresql.Driver")
        )

        logging.info("Returning spark_reader object. Apply '.load()' method to trigger.")
        return spark_reader

    @staticmethod
    def jdbc_writer(dataframe: pyspark.sql.DataFrame,dbname, table_name, pg_sdk_connector: PostgresConnector=None, write_mode=PostgresWriteMode.APPEND) -> pyspark.sql.DataFrameWriter:

        pg_creds=None
        if pg_sdk_connector:
            logging.info('Fetching url and properties from pg_sdk_connector')
            pg_creds = pg_sdk_connector.get_postgres_creds()
            jdbc_url = f"jdbc:postgresql://{pg_creds.hosts}:{pg_creds.port}/{dbname}?sslmode=require"  
    
        logging.info('Write from Spark JDBC')

        spark_writer = (
            dataframe.write
                .format('jdbc')
                .option('url', jdbc_url)
                .option('dbtable', table_name)
                .option('user', pg_creds.user)
                .option('password', pg_creds.code)
                .option('driver', 'org.postgresql.Driver')
                .mode(write_mode)
        )

        logging.info("Returning spark_writer object. Apply '.save()' method to trigger.")
        return spark_writer