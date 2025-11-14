from googleads import ad_manager
from kuber_data_sync.configs import CommonConfigs, GAMConfigs, MongoConfigs, SyncMode
from delta_sdk.utils.common import CommonUtils
from delta_sdk.utils.common import RateLimiter
from datetime import datetime
from kuber_data_sync.model.time import DateTime
import pytz
import zeep
import pymongo
import copy
from pydantic import ValidationError
from kuber_data_sync.exceptions import ExceptionLogging, MissingDependencies
from kuber_data_sync.report import Report
from delta_sdk.utils import logging

class BaseEntity:

    gam_service_name: str
    gam_pagination_limit = 1000
    gam_batch = 0
    dependent_entities = set()
    primary_search_key = "_id"
    ERASE_BEFORE_INSERT = False
    FULL_REFRESH_INTERVAL_IN_SECONDS = 3600
    filter = {}

    @classmethod
    def build_statement(cls, *args, **kwargs):
        try:
            logging.info("Returning default Statement as no Custom statement configured.")
            return cls.statement
        except Exception as e:
            logging.error(f"Error in BaseEntity.build_statement: {type(e).__name__}: {e}")
            raise

    @classmethod
    @CommonUtils.retry_connection(
        max_retries=4, delay=1, delay_type='exponential',
        rate_limiter=RateLimiter(
            name='kuber_data_sync', mode=RateLimiter.mode.BY_CEILING,
            ceiling=15, time_window=60
            ))
    def fetch(cls, mongo_client=None, gam_client=None,  *args, **kwargs):
        """Fetch records for respective entities from GAM.
        Args::
            gam_client
        Response::
            Yielding records in batches as configured.
        Note::
        """
        try:
            logging.info("Inside 'fetch' block.")
            service = gam_client.GetService(service_name=cls.gam_service_name, version=GAMConfigs.GAM_VERSION)
            """Builds GAM statement only if refresh interval has passed."""
            # cls.start_date: datetime = datetime(2022, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(CommonConfigs.TIMEZONE))
            cls.statement = copy.deepcopy((
            ad_manager
            .StatementBuilder(version=GAMConfigs.GAM_VERSION)
            .Limit(cls.gam_pagination_limit)
            ))
            cls.build_statement(mongo_client=mongo_client, gam_client=gam_client)
            service_method = getattr(service, cls.gam_method_name)
            logging.info(f"Method to be called:- {cls.gam_service_name}.{cls.gam_method_name}")

            offset = 0
            while True:
                statement_query = cls.statement.ToStatement()
                logging.info(f'Statement Query: {statement_query}')
                response = service_method(statement_query)
                response = zeep.helpers.serialize_object(response)
                # logging.info(f"Full GAM Response: {response}")
                if result := response.get('results'):
                    yield result
                    offset += cls.gam_pagination_limit
                    cls.statement.Offset(offset)
                    cls.gam_batch += 1
                else:
                    logging.info(f"No more {cls.__name__} to fetch.")
                    cls.gam_batch = 0
                    break
            logging.info(f"Fetching from {cls.__name__} complete")
        except Exception as e:
            logging.error(f"Error in BaseEntity.fetch: {type(e).__name__}: {e}")
            raise


    @classmethod
    def get_external_internal_id_map_mongo(cls, mongo_client, ids: list) -> dict:
        """
        Args::
            mongo_client:
            ids: list of external ids
        Returns::
            external_internal_ad_id_map: Map which has a map of externalId (for GAM) to internalID (for mongo campaign-manager db)
        Note::
            Useful when we want to recreate the relations created in GAM , in 'campaign-manager' DB .
        """
        try:
            filter = {"externalId": {"$in": ids}}
            projection = {"externalId":1, "_id": 1}
            id_list = mongo_client[MongoConfigs.DB_NAME][cls.mongo_collection_name].find(filter=filter,projection=projection)
            external_internal_ad_id_map = {ad['externalId']:ad['_id'] for ad in id_list}
            logging.info(f"External id to internal id map generated for :- {external_internal_ad_id_map}")
            return external_internal_ad_id_map
        except Exception as e:
            logging.error(f"Error in BaseEntity.get_external_internal_id_map_mongo: {type(e).__name__}: {e}")
            raise

    @classmethod
    def batch_gen(cls, records, batch_size: int=1000, start: int=0, limit=float('inf')):
        try:
            limit = min(limit, len(records))
            batch_no = 0
            for index in range(start, limit, batch_size):
                start = index
                end = min(index+batch_size+1, limit)
                batch_no += 1
                yield records[start:end]
                logging.info(f"GAM Batch:{cls.gam_batch} Mongo Batch:{batch_no} read from index {cls.gam_pagination_limit*cls.gam_batch + start+1} to {cls.gam_pagination_limit*cls.gam_batch + end } completed.")
        except Exception as e:
            logging.error(f"Error in BaseEntity.batch_gen: {type(e).__name__}: {e}")
            raise

    @classmethod
    def write_to_mongo(cls, mongo_client, records: list[dict]):
        """
        Args::
            records: preprocessed records fetched from GAM.
            mongo_client: 
        Note::
            -> Skips updating Mongo if `updateTime` is unchanged and present.
            -> If `updateTime` is not in any record, assume all are new or changed.
        """
        try:
            logging.info(f"Writing to mongo coll: {cls.mongo_collection_name}")
            collection = mongo_client[MongoConfigs.DB_NAME][cls.mongo_collection_name]

            for batch in cls.batch_gen(records, batch_size=1000):
                bulk_operations = []

                # Check if updateTime is present in any record in the batch
                has_update_time = any("updateTime" in record for record in batch)

                existing_map = {}
                if has_update_time:
                    # Step 1: Extract primary keys
                    batch_ids = [record[cls.primary_search_key] for record in batch]
                    
                    # Step 2: Bulk fetch existing records
                    existing_docs = collection.find(
                        {cls.primary_search_key: {"$in": batch_ids}},
                        {cls.primary_search_key: 1, "updateTime": 1}
                    )
                    existing_map = {doc[cls.primary_search_key]: doc.get("updateTime") for doc in existing_docs}

                # Step 3: Iterate through batch and prepare upserts
                for record in batch:
                    record_id = record[cls.primary_search_key]

                    if has_update_time:
                        existing_update_time = existing_map.get(record_id)
                        if existing_update_time == record.get("updateTime"):
                            logging.debug(f"Skipping upsert for {cls.__name__} ID {record_id} — no change in updateTime.")
                            continue

                    # Add lastRefreshDateTime
                    record["lastRefreshDateTime"] = DateTime.get_current_datetime_with_millis()

                    bulk_operations.append(
                        pymongo.UpdateOne(
                            {cls.primary_search_key: record_id},
                            {"$set": record},
                            upsert=True
                        )
                    )

                if bulk_operations:
                    result = collection.bulk_write(bulk_operations).bulk_api_result
                    Report.update_entity_mongo_stats(entity=cls.__name__, data=result)
                else:
                    logging.info("No changes detected in this batch — skipping bulk write.")

            logging.info(f"BulkWrite for {cls.mongo_collection_name} collection complete.")
        except Exception as e:
            logging.error(f"Error in BaseEntity.write_to_mongo: {type(e).__name__}: {e}")
            raise

    @classmethod
    def clear_mongo_collection(cls, mongo_client):
        """
        Deletes documents matching a filter in the target MongoDB collection 
        if ERASE_BEFORE_INSERT is True, and verifies that no matching documents remain.

        Args:
            mongo_client: MongoDB client instance.
        """
        try:
            if cls.ERASE_BEFORE_INSERT:
                collection = mongo_client[MongoConfigs.DB_NAME][cls.mongo_collection_name]
                result = collection.delete_many(cls.filter)
                remaining_count = collection.count_documents(cls.filter)
                
                if remaining_count == 0:
                    logging.info(
                        f"Successfully cleared {result.deleted_count} documents from collection '{cls.mongo_collection_name}' matching filter {cls.filter}"
                    )
                else:
                    raise RuntimeError(
                        f"Failed to clear all filtered documents from collection '{cls.mongo_collection_name}'. {remaining_count} documents matching filter remain."
                    )
        except Exception as e:
            logging.error(f"Error in BaseEntity.clear_mongo_collection: {type(e).__name__}: {e}")
            raise

    @classmethod
    def validate_and_transform(cls, preprocessed_records: list[dict], gam_client=None, mongo_client=None, exclude={}) -> list[dict]:
        """Massage the data as per the respective models.
        Args::
            preprocessed_records: preprocessed_records fetched from GAM.
            mongo_client: 
            gam_client: 
            exclude: set of fields which are used in processing but need to be ignored during dumping.
        Returns::
            processed_records: processed records.
        Note::
            :by_alias: True by default. for renaming output as per the `serialization_class`
        """
        try:
            logging.info("Inside 'validate_and_transform' block.")
            processed_records = []
            for record in preprocessed_records:
                try:
                    # logging.info(f"before: {record}")
                    record = cls.model(**record).model_dump(by_alias=True, exclude_none=True)
                    # logging.info(f"after: {record}")
                    processed_records.append(record)
                
                except ValidationError as e:
                    ExceptionLogging.log_error(
                        mongo_client=mongo_client,
                        entityType=cls.__name__,
                        error_log=e,
                        exceptionType=type(e).__name__
                        )
                    logging.error(f"{type(e).__name__} : {e}")
            return processed_records
        except Exception as e:
            logging.error(f"Error in BaseEntity.validate_and_transform: {type(e).__name__}: {e}")
            raise

    @classmethod
    def post_processing(cls,*args, **kwargs):
        """Default Post Processing method."""
        try:
            logging.info("No Post processing required.")
            pass
        except Exception as e:
            logging.error(f"Error in BaseEntity.post_processing: {type(e).__name__}: {e}")
            raise

    @classmethod
    def sync(cls, mongo_client, gam_client, synched_entities: set[str]=set()):
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
        sync_status = False
        error_message = ''
        try:
            
            # ✅ NEW: Clear Mongo collection if ERASE_BEFORE_INSERT is True
            if getattr(cls, 'ERASE_BEFORE_INSERT', False):
                cls.clear_mongo_collection(mongo_client)
                logging.info(f"Cleared Mongo collection for {cls.__name__} as ERASE_BEFORE_INSERT is True.")
                
            # Check if a refresh is needed before proceeding
            if hasattr(cls, "should_refresh") and not cls.should_refresh(mongo_client):
                logging.info("Skipping fetch — not enough time has passed.")
                sync_status = True
                return sync_status   
            
            # If the class is Package, stop execution after clearing collection
            if cls.__name__ == "Package":
                sync_status = True
                return sync_status


            logging.info(f"Starting sync method for {cls.__name__}")
            if not cls.dependent_entities.issubset(synched_entities):
                missing_dependent_entities = list(cls.dependent_entities-synched_entities)
                raise MissingDependencies(
                    entityType=cls.__name__,
                    mongo_client=mongo_client,  
                    message=f"Following dependent entities not synched yet.:- {', '.join(missing_dependent_entities)}"
                    )

            for gam_records in cls.fetch(gam_client=gam_client, mongo_client=mongo_client):
                logging.info(f"Print 1 record: {gam_records[:1]}")
                records = cls.validate_and_transform(preprocessed_records=gam_records, mongo_client=mongo_client, gam_client=gam_client)
                cls.write_to_mongo(mongo_client=mongo_client, records=records)
                cls.post_processing(processed_records=records, mongo_client=mongo_client)
            sync_status = True

        except Exception as e:
            logging.error(f"Failed during the sync of {cls.__name__}")
            error_message = f"{type(e).__name__}: {e}"
            logging.error(error_message)
            ExceptionLogging.log_error(mongo_client=mongo_client, entityType=cls.__name__, error_log=e, exceptionType=type(e).__name__)
            sync_status = False
            raise

        finally:
            Report.update_entity_sync_status(entity=cls.__name__, status=sync_status, error_message=error_message)
            Report.show_entity_report(entity=cls.__name__)
            return sync_status