from datetime import datetime, timedelta
import pytz
from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.configs import MongoConfigs
from kuber_data_sync.model.models import LineItemModel
from kuber_data_sync.service.order import Order
from kuber_data_sync.service.package import Package
from delta_sdk.utils import logging
from kuber_data_sync.configs import SyncMode, CommonConfigs
from kuber_data_sync.exceptions import MissingInternalIdError

__all__ = ["LineItem"]

class LineItem(BaseEntity):

    gam_service_name = 'LineItemService'
    gam_method_name = "getLineItemsByStatement"
    mongo_collection_name = "lineitem"
    model = LineItemModel
    dependent_entities = { "Advertiser", "Order" }
    primary_search_key = "externalId"
    
    @classmethod
    def build_statement(cls, *args, **kwargs):

        if CommonConfigs.SYNC_MODE == SyncMode.ALL:
            # cls.statement = (
            #     cls.statement
            #     .Where("lastModifiedDateTime >= :startDateForSync")
            #     .WithBindVariable('startDateForSync', cls.start_date)
            # )
            cls.statement = (
                cls.statement
            )
            return

        date_filter = datetime.now(pytz.timezone(CommonConfigs.TIMEZONE)) - timedelta(hours=CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS)
        logging.info(f'Filter added to get records for last {CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS} hours. Since: {date_filter}')
        
        cls.statement = (
            cls.statement
            .Where("lastModifiedDateTime >= :lastModifiedDateTime")
            .WithBindVariable('lastModifiedDateTime', date_filter)
        )
    
    @classmethod
    def validate_and_transform(cls, preprocessed_records, gam_client=None, mongo_client=None):
        """
        Note::
            ++ Fetch internal ids for the following fields from the external ids :- orderId, advertiserId, packageId
            ++ Add foreign key ids fields :- orderId, advertiserId, packageId referring to respective internal collections
            ++ Trigger Order sync service by order_ids after fetching the list from LineItem records data.
        """


        logging.info("Fetching Order records from mongo")
        ext_order_ids_list = [ str(record['orderId']) for record in preprocessed_records ]
        filter = { "externalId": {"$in": ext_order_ids_list } }
        projection = { "externalId":1, "_id": 1, "advertiserId":1 }
        order_records = list(mongo_client[MongoConfigs.DB_NAME][Order.mongo_collection_name].find(filter=filter,projection=projection))

        logging.info("Fetching Package records from mongo")
        filter = { "orderId": {"$in": list([record['_id'] for record in order_records ]) } }
        projection = { "orderId":1, "_id": 1, "advertiserId": 1 }
        package_records = list(mongo_client[MongoConfigs.DB_NAME][Package.mongo_collection_name].find(filter=filter,projection=projection))

        ext_2_int_id_map = {
            "Order": {
                    "Order": { record['externalId']:record['_id'] for record in order_records }
                }
        }

        int_2_int_id_map = {
            "Order": {
                "Package": { record['orderId']:record['_id'] for record in package_records },
                "Advertiser": { record['_id']:record['advertiserId'] for record in order_records }
            }
        }

        for record in preprocessed_records:

            try:

                ext_order_id = record["orderId"]
                int_order_id = ext_2_int_id_map["Order"]["Order"].get(str(ext_order_id))

                if int_order_id:
                    record['orderId'] = int_order_id
                else:
                    raise MissingInternalIdError(destEntityType=cls.__name__, sourceEntityType="Order",
                                                missingDestField="orderId", missingSourceField="_id",
                                                originaldestValue=ext_order_id,
                                                mongo_client=mongo_client)

                if int_id:=int_2_int_id_map["Order"]["Advertiser"].get(int_order_id):
                    record['advertiserId'] = int_id
                else:
                    raise MissingInternalIdError(destEntityType=cls.__name__, sourceEntityType="Order",
                                                missingDestField="advertiserId", missingSourceField="advertiserId",
                                                sourceEntityExtId=ext_order_id,
                                                mongo_client=mongo_client)

                if int_id:=int_2_int_id_map["Order"]["Package"].get(int_order_id):
                    record['packageId'] = int_id
                else:
                    raise MissingInternalIdError(destEntityType=cls.__name__, sourceEntityType="Package",
                                                missingDestField="packageId", missingSourceField="orderId",
                                                sourceEntityExtId=ext_order_id,
                                                mongo_client=mongo_client)

            except MissingInternalIdError as e:
                # logging.error(f"{type(e).__name__}:{e}")
                pass

        return super().validate_and_transform(gam_client=gam_client, mongo_client=mongo_client, preprocessed_records=preprocessed_records)