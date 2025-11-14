from delta_sdk.utils import logging
from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.model.models import AdUnitModel
from kuber_data_sync.configs import SyncMode, CommonConfigs
from datetime import datetime, timedelta
import pytz
__all__ = ["AdUnit"]

class AdUnit(BaseEntity):

    gam_service_name = 'InventoryService'
    gam_method_name = 'getAdUnitsByStatement'
    mongo_collection_name = "adUnits"
    model = AdUnitModel
    primary_search_key = "externalId"

    @classmethod
    def build_statement(cls, *args, **kwargs):
        if CommonConfigs.SYNC_MODE == SyncMode.ALL:
            cls.statement = (
                cls.statement
                .Where("status = :status")
                .WithBindVariable('status', 'ACTIVE')
            )
            return

        date_filter = datetime.now(pytz.timezone(CommonConfigs.TIMEZONE)) - timedelta(hours=CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS)
        logging.info(f'Filter added to get records for last {CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS} hours. Since: {date_filter}')
        
        cls.statement = (
            cls.statement
            .Where("status = :status")
            .Where("lastModifiedDateTime >= :lastModifiedDateTime")
            .WithBindVariable("status", 'ACTIVE')
            .WithBindVariable("lastModifiedDateTime", date_filter)
        )
        