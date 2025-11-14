from delta_sdk.utils import logging
from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.model.models import BandwidthGroupModel

from googleads import ad_manager
from kuber_data_sync.configs import CommonConfigs, GAMConfigs, MongoConfigs
from datetime import datetime
import pytz
import zeep
import copy
from pytz import timezone, utc
from kuber_data_sync.model.time import DateTime

__all__ = ["BandwidthGroup"]

class BandwidthGroup(BaseEntity):

    gam_service_name = 'PublisherQueryLanguageService'
    gam_method_name = 'select'
    mongo_collection_name = "bandwidthGroup"
    model = BandwidthGroupModel

    @classmethod
    def build_statement(cls, *args, **kwargs):
        logging.info("Building PQL to fetch targetable Bandwidth_Group.")

        cls.statement = (
            cls.statement
            .Select("Id, BandwidthName")
            .From("Bandwidth_Group")
        )
        
        
    @classmethod
    def should_refresh(cls, mongo_client) -> bool:
        """Checks whether a full refresh is needed based on lastRefreshDateTime."""
        db = mongo_client[MongoConfigs.DB_NAME]
        collection = db[cls.mongo_collection_name]

        # Get the latest lastRefreshDateTime
        latest = list(
            collection.find(
                filter={"lastRefreshDateTime": {"$exists": True}},
                projection={"lastRefreshDateTime": 1, "_id": 0}
            ).sort("lastRefreshDateTime", -1).limit(1)
        )

        if not latest:
            logging.info("No lastRefreshDateTime found. Proceeding with full refresh.")
            return True

        latest_refresh = latest[0]["lastRefreshDateTime"]
        if latest_refresh.tzinfo is None:
            # Assume it's in local timezone and convert to aware
            latest_refresh = timezone(CommonConfigs.TIMEZONE).localize(latest_refresh)

        now = DateTime.get_current_datetime_with_millis()
        elapsed_seconds = (now - latest_refresh).total_seconds()
        logging.info(f"Latest refresh: {latest_refresh} | Now: {now} | Elapsed: {elapsed_seconds}s")
        return elapsed_seconds >= cls.FULL_REFRESH_INTERVAL_IN_SECONDS

    @classmethod
    def fetch(cls, mongo_client=None, gam_client=None, *args, **kwargs):
        logging.info("Inside overridden 'fetch' block for BandwidthGroup.")
        service = gam_client.GetService(service_name=cls.gam_service_name, version=GAMConfigs.GAM_VERSION)

        cls.start_date = datetime(2022, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(CommonConfigs.TIMEZONE))
        cls.statement = copy.deepcopy(
            ad_manager.StatementBuilder(version=GAMConfigs.GAM_VERSION).Limit(cls.gam_pagination_limit)
        )
        cls.build_statement(mongo_client=mongo_client, gam_client=gam_client)
        service_method = getattr(service, cls.gam_method_name)

        offset = 0

        while True:
            statement_query = cls.statement.ToStatement()
            logging.info(f"Statement Query: {statement_query}")

            response = service_method(statement_query)
            response = zeep.helpers.serialize_object(response)

            rows = response.get("rows", [])
            if not rows:
                logging.info(f"No more {cls.__name__} to fetch.")
                cls.gam_batch = 0
                break

            batch = []
            for row in rows:
                values = row.get('values', [])
                record = {}

                try:
                    # Id (Long)
                    if len(values) > 0 and values[0].get('value') is not None:
                        record["Id"] = str(values[0]['value'])

                    # Name (String)
                    if len(values) > 1 and values[1].get('value'):
                        record["BandwidthName"] = str(values[1]['value'])

                    batch.append(record)
                except Exception as e:
                    logging.error(f"Failed to parse row: {row} with error: {e}")
                    continue

            yield batch
            offset += cls.gam_pagination_limit
            cls.statement.Offset(offset)
            cls.gam_batch += 1

        logging.info(f"Fetching from {cls.__name__} complete.")
