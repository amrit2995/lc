from delta_sdk.utils import logging
from datetime import datetime, timedelta
import pytz
from kuber_data_sync.configs import SyncMode
from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.service.advertiser import Advertiser
from kuber_data_sync.model.models import OrderModel
from kuber_data_sync.configs import MongoConfigs, CommonConfigs
from kuber_data_sync.service.package import Package
from kuber_data_sync.exceptions import MissingInternalIdError

__all__ = ["Order"]

class Order(BaseEntity):

    gam_service_name = 'OrderService'
    gam_method_name = 'getOrdersByStatement'
    mongo_collection_name = "order"
    model = OrderModel
    dependent_entities = { "Advertiser" }
    primary_search_key = "externalId"

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
            .WithBindVariable('lastModifiedDateTime', date_filter)
        )
        
        
    @classmethod
    def validate_and_transform(cls, preprocessed_records: list, mongo_client=None, gam_client=None):

        ext_advertiser_ids_list = [ str(record['advertiserId']) for record in preprocessed_records ]
        ext_2_int_map = {
            "Advertiser":
                {
                    "Advertiser": Advertiser.get_external_internal_id_map_mongo(mongo_client=mongo_client, ids=ext_advertiser_ids_list)
                }
        }

        for record in preprocessed_records:

            try:
                if int_id:=ext_2_int_map["Advertiser"]["Advertiser"].get(str(record["advertiserId"])):
                    record['advertiserId'] = int_id
                else:
                    raise MissingInternalIdError(destEntityType=cls.__name__, sourceEntityType="Advertiser",
                                                missingDestField="advertiserId", missingSourceField="_id",
                                                sourceEntityExtId=record['advertiserId'],
                                                mongo_client=mongo_client)
            except MissingInternalIdError as e:
                # logging.error(f"{type(e).__name__}:{e}")
                pass

        return super().validate_and_transform(preprocessed_records=preprocessed_records, mongo_client=mongo_client)

    @classmethod
    def post_processing(cls, mongo_client, processed_records):

        logging.info("Implementing post processing logic.")

        ext_order_ids_list = [ str(record['externalId']) for record in processed_records ]

        filter = {"externalId":{ "$in": ext_order_ids_list }}
        projection = {"externalId": 1, "_id":1}
        order_records = mongo_client[MongoConfigs.DB_NAME][cls.mongo_collection_name].find(filter=filter, projection=projection)


        ext_2_int_id_map = {
            "Order":
                {
                    "Order": { record["externalId"]: record["_id"] for record in order_records }
                }
        }

        logging.info("Fetching packages by OrderId.")
        int_order_ids_list = list(ext_2_int_id_map["Order"]["Order"].values())
        filter = { "orderId": { "$in": int_order_ids_list } }
        projection = {"_id": 1, "orderId": 1}
        package_records = mongo_client[MongoConfigs.DB_NAME][Package.mongo_collection_name].find(filter=filter, projection=projection)


        int_2_int_id_map = {
            "Order":
                {
                    "Package": { record["orderId"]: record["_id"] for record in package_records }
                }
        }

        logging.info("Creating Package if package donot exists.")
        for record in processed_records:
            int_order_id = ext_2_int_id_map["Order"]["Order"].get(str(record['externalId']))

            if not int_2_int_id_map["Order"]["Package"].get(int_order_id):

                Package.create(
                    name=f"{record['name']}_PACKAGE",
                    orderId=int_order_id,
                    advertiserId=record["advertiserId"]
                )
            
        Package.mongo_create_dump(mongo_client=mongo_client)
        return True