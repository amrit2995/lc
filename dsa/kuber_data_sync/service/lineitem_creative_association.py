from delta_sdk.utils import logging
from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.service.lineitem import LineItem
from kuber_data_sync.service.creative import Creative
from kuber_data_sync.model.models import LineItemCreativeAssociationModel
from kuber_data_sync.exceptions import MissingInternalIdError
from kuber_data_sync.configs import SyncMode, CommonConfigs
from datetime import datetime, timedelta
import pytz

__all__ = ["LineItemCreativeAssociation"]

class LineItemCreativeAssociation(BaseEntity):

    gam_service_name = 'LineItemCreativeAssociationService'
    gam_method_name = 'getLineItemCreativeAssociationsByStatement'
    mongo_collection_name = "lineItemCreativeAssociation"
    model = LineItemCreativeAssociationModel
    dependent_entities = { "Advertiser", "Order", "LineItem", "Creative" }
    primary_search_key = "creativeId"

    @classmethod
    def build_statement(cls, *args, **kwargs):
        if CommonConfigs.SYNC_MODE == SyncMode.ALL:
            cls.statement = (
                cls.statement
            )
            return

        date_filter = datetime.now(pytz.timezone(CommonConfigs.TIMEZONE)) - timedelta(hours=CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS)
        logging.info(f'Filter added to get records for last {CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS} hours. Since: {date_filter}')
        
        cls.statement = (
            cls.statement
            .Where("lastModifiedDateTime >= :lastModifiedDateTime")
            .WithBindVariable("lastModifiedDateTime", date_filter)
        )
        
    @classmethod
    def validate_and_transform(cls, preprocessed_records, mongo_client, **kwargs):
        """
            ++ Replaces the gam external ids of 'lineItemId' and 'creativeId' with resoective mongo internal ids.
            ++ Trigger sync for list of external LineItems that were foudn during fetching of LineItemCreativeAssociationService
        """


        ext_creative_ids = [ str(record['creativeId']) for record in preprocessed_records ]
        ext_lineitem_ids = [ str(record['lineItemId']) for record in preprocessed_records ]

        logging.info("Generating external 2 internal ids maps")
        ext_2_int_map = {
            "LineItem":{
                    "LineItem": LineItem.get_external_internal_id_map_mongo(mongo_client=mongo_client, ids=ext_lineitem_ids)
                },
            "Creative":{
                "Creative": Creative.get_external_internal_id_map_mongo(mongo_client=mongo_client, ids=ext_creative_ids)
            }
        }

        for record in preprocessed_records:
            try:
                if int_id:=ext_2_int_map["LineItem"]["LineItem"].get(str(record["lineItemId"])):
                    record['lineItemId'] = str(int_id)
                else: 
                    raise MissingInternalIdError(destEntityType=cls.__name__, sourceEntityType="LineItem",
                                                missingDestField="lineItemId", missingSourceField="_id",
                                                originaldestValue=record["lineItemId"],
                                                mongo_client=mongo_client)

                if int_id:=ext_2_int_map["Creative"]["Creative"].get(str(record["creativeId"])):
                    record['creativeId'] = str(int_id)
                else:
                    raise MissingInternalIdError(destEntityType=cls.__name__, sourceEntityType="LineItem",
                                                missingDestField="creativeId", missingSourceField="_id",
                                                originaldestValue=record["creativeId"],
                                                mongo_client=mongo_client)
                    
                # To do Backfill for Creative and LineiTem Service

            except Exception as e:
                # logging.error(f"{type(e).__name__}:{e}")
                continue

        return super().validate_and_transform(preprocessed_records=preprocessed_records)