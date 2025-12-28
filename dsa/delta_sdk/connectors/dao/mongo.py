import pymongo.collection, pymongo.errors as errors
from delta_sdk.connectors.base import BaseConnector
# from delta_sdk.configs.common import MONGO_DATAPROC_PROPERTIES
import pymongo
from delta_sdk.configs.connConfigs import MONGO
from delta_sdk.utils import logging
from delta_sdk.utils.common import CommonUtils

class MongoCreds:
    def __init__(self, host, ca_path, truststore_code):
        self.host = host
        self.ca_path = ca_path
        self.truststore_code = truststore_code

    def __call__(self, key=None):
        if hasattr(self, key):
            return getattr(self, key)
        return {'host': self.host, 'ca_path': self.ca_path}

    def __repr__(self):
        return f"MongoCreds(host={self.host}, ca_path={self.ca_path}), truststore_code={self.truststore_code}"

    def get_servers_list(self):
        import re
        host_str = self.host
        servers = re.findall(r'([\w.-]+:\d+)', host_str)
        return servers

class MongoWriteMode:
    OVERWRITE = 'overwrite'
    APPEND = 'append'

    @classmethod
    def list_modes(cls):
        return [cls.OVERWRITE, cls.APPEND]


class MongoConnector(BaseConnector):
    def __init__(self, 
                env: str = '',
                clusterName: str ='', 
                nucleusHash: str ='',
                base_path: str='',
                region: str ='east'):
        super().__init__(env=env, applicationName=MONGO["applicationName"][env], scope=MONGO["scope"][clusterName],
                          nucleusHash=nucleusHash, base_path=base_path, region=region)
        self._client = None
        self._mongo_creds = None

    def get_mongo_creds(self) -> MongoCreds:

        data = self.get_creds()
        ca_path = self._createCredsFile(data=data['ca'], file_name='caFile.pem')
        host = data['host']
        truststore_code = data.get('trustorePassword', '')

        mongo_creds = MongoCreds(
            host=host,
            ca_path=ca_path,
            truststore_code=truststore_code
        )
        logging.info(mongo_creds)
        return mongo_creds

    @CommonUtils.retry_connection(max_retries=2, delay=1)
    def get_client(self) -> pymongo.MongoClient:
        try:
            if not self._client:

                logging.info("Connecting to Remote Host")
                mongo_creds = self.get_mongo_creds()
                self._client = pymongo.MongoClient(mongo_creds.host,
                    tls=True,
                    tlsCAFile=mongo_creds.ca_path
                    )
                logging.info("Mongo server details:")
                logging.info(self._client.server_info())

            return self._client
        except Exception as e:
            logging.error(f"{type(e).__name__}:  {str(e)}")

    @property
    def client(self):
        return self.get_client()

    # def get_dataproc_spark_properties(self):
    #     creds = self.get_mongo_creds()
    #     mongo_dataproc_properties = MONGO_DATAPROC_PROPERTIES

    #     for property in ["spark.driver.extraJavaOptions", "spark.executor.extraJavaOptions"]:
    #         mongo_dataproc_properties[property] = (
    #             mongo_dataproc_properties["spark.driver.extraJavaOptions"]
    #             .replace("<trust_store_code>", creds.truststore_code)
    #             .replace("<key_store_code>", creds.keystore_code)
    #             .replace("<trust_store_cert_path>", f"./{CERTS['gcs_bucket']['mongo'][self.clusterName][self.env]['trustStorePath'].split('/')[-1]}")
    #             .replace("<key_store_cert_path>", f"./{CERTS['gcs_bucket']['mongo'][self.clusterName][self.env]['keyStorePath'].split('/')[-1]}")
    #         )
    #     return mongo_dataproc_properties

class MongoOperators:

    @staticmethod
    def truncate_table(collection: pymongo.collection.Collection):
        try:
            collection.delete_many({})
            logging.info("Deleting all old Mongo records.")
        except Exception as e:
            logging.info(f"Failed to delete table : {e}")

    @staticmethod
    def read_in_batch_gen(collection: pymongo.collection.Collection, filter={}, projection={}, batch_size=1000, limit=float('inf'), start=0):

        try:
            batch_no = 0            
            base_cursor = collection.find(filter=filter, projection=projection)
            for index in range(start, batch_size, limit):
                batch_cursor = base_cursor.skip(index).limit(batch_size+1)
                yield list(batch_cursor)
                batch_no += 1

        except StopIteration:
            if batch_no == 0:
                raise Exception("No documents found for the query")
            else:
                logging.info("All data for the query complete")

        except Exception as e:
            logging.info(e)

    @staticmethod
    def write_in_batch(collection: pymongo.collection.Collection=None, batch_size=100, docs=None):
        batch_no = 0

        for start_index in range(0, len(docs), batch_size):
            try:
                batch = docs[start_index:start_index + batch_size]
                result = collection.insert_many(batch)
                logging.info(f'Batch {batch_no} write complete')
                batch_no += 1
            except errors.BulkWriteError as bwe:
                logging.info(f"Bulk write error: {bwe.details}")
            except Exception as e:
                logging.info(f"An error occurred: {e}")

# class SparkMongoOperators:

#     @staticmethod
#     def reader(database_name, collection_name, mongo_sdk_connector: MongoConnector, readSchema=None, spark: pyspark.sql.SparkSession=None):

#         if mongo_sdk_connector:
#             mongo_creds = mongo_sdk_connector.get_mongo_creds()


#         spark_reader = (
#             spark.read
#             .format("mongodb")
#             .option("spark.mongodb.read.connection.uri", mongo_creds.host)
#             .option("spark.mongodb.read.database", database_name)
#             .option("spark.mongodb.read.collection", collection_name)
#             .option("spark.mongodb.ssl.enabled", "true")
#             .load()
#         )

#         if readSchema:
#             spark_reader = spark_reader.schema(readSchema)
        
#         logging.info(f"spark reader: {spark_reader}")
#         logging.info(f'Returning spark reader object. Exceute by <reader_object>.load() to trigger.')
#         return spark_reader

#     @staticmethod
#     def writer(dataframe: pyspark.sql.dataframe.DataFrame, database_name, collection_name, write_mode=MongoWriteMode.APPEND, mongo_sdk_connector: MongoConnector=None):

#         if mongo_sdk_connector:
#             mongo_uri = mongo_sdk_connector.get_mongo_creds().host
#         if not mongo_uri:
#             raise ValueError(f'Niether "mongo_uri" nor "mongo_sdk_connector" provided.')

#         spark_writer = (
#         dataframe.write
#             .format("mongodb")
#             .option("spark.mongodb.write.connection.uri", mongo_uri)
#             .option("spark.mongodb.write.database", database_name)
#             .option("spark.mongodb.write.collection", collection_name)
#             .mode(write_mode)
#         )
        
#         logging.info(f'Returning spark writer object. Exceute by <writer_object>.save() to trigger.')
#         return spark_writer