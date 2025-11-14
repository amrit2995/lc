from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.model.models import TraffickerModel
from delta_sdk.utils import logging
from kuber_data_sync.configs import CommonConfigs, MongoConfigs
from pytz import timezone
from kuber_data_sync.model.time import DateTime
from delta_sdk.utils import logging


__all__ = ["Trafficker"]

class Trafficker(BaseEntity):

    gam_service_name = 'UserService'
    gam_method_name = 'getUsersByStatement'
    mongo_collection_name = "trafficker"
    model = TraffickerModel
    
    @classmethod
    def build_statement(cls, *args, **kwargs):

        logging.info("Adding filter to find only 'Active' traffickers.")
        cls.statement = (
            cls.statement
            .Where("status = :status")
            .WithBindVariable('status', 'ACTIVE')
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
