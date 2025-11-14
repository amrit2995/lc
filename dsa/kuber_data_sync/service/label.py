from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.model.models import LabelModel
from delta_sdk.utils import logging
from kuber_data_sync.configs import CommonConfigs, MongoConfigs
from pytz import timezone
from kuber_data_sync.model.time import DateTime

__all__ = ["Label"]

class Label(BaseEntity):

    gam_service_name = "LabelService"
    gam_method_name = "getLabelsByStatement"
    mongo_collection_name = "label"
    model = LabelModel
    
    @classmethod
    def build_statement(cls, *args, **kwargs):

        cls.statement = (
            cls.statement
            .Where("(types = :ad_exclusion OR types= :competitive_exclusion) AND isActive=:is_active")
            .WithBindVariable("ad_exclusion", "AD_EXCLUSION")
            .WithBindVariable("competitive_exclusion", "COMPETITIVE_EXCLUSION")
            .WithBindVariable("is_active", "true")
        )

        logging.info("Added filter to filter by. 'active', type :'ad_exclusion' or 'competitive_exclusion', and :- ")
        
          
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
