import pytz

from delta_sdk.utils import logging
from kuber_data_sync.service.base import BaseEntity
from datetime import datetime, timedelta
from kuber_data_sync.configs import SyncMode, CommonConfigs
from kuber_data_sync.service.advertiser import Advertiser
from kuber_data_sync.service.creative_template import CreativeTemplate
from kuber_data_sync.model.models import CreativeModel
from kuber_data_sync.configs import CommonConfigs

__all__ = ["Creative"]

class Creative(BaseEntity):

    gam_service_name = 'CreativeService'
    gam_method_name = 'getCreativesByStatement'
    mongo_collection_name = "creative"
    model = CreativeModel
    dependent_entities = { "Advertiser", "Order" }
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
            .WithBindVariable("lastModifiedDateTime", date_filter)
        )
    
    @classmethod
    def validate_and_transform(cls, preprocessed_records, gam_client=None, mongo_client=None):
        f"""
            ++ Replaces the foreign key 'advertiserId' from gam externalId to mongo internal id reffering to {Advertiser.mongo_collection_name} collection.
        """

        ext_ads_ids_list = [ str(record['advertiserId']) for record in preprocessed_records ]
        ext_2_int_map = {
            "advertiserId":
                {
                    "advertiserId": Advertiser.get_external_internal_id_map_mongo(mongo_client=mongo_client, ids=ext_ads_ids_list)
                }
        }
        for record in preprocessed_records:
            record["advertiserId"] = ext_2_int_map['advertiserId']['advertiserId'].get(str(record["advertiserId"]), "INT_ID_NOT_FOUND")
            
        template_ids = [
            str(record.get('templateId') or record.get('creativeTemplateId'))
            for record in preprocessed_records
            if record.get('templateId') or record.get('creativeTemplateId')
        ]
        logging.info("Generating template_variable_type maps")
        templateVariableTypeMap = CreativeTemplate.get_template_variable_type_map_mongo(mongo_client=mongo_client, ids=template_ids)
        for record in preprocessed_records:
            template_id = str(record.get('templateId') or record.get('creativeTemplateId'))
            if not template_id:
                logging.warning(f"No templateId found for record: {record.get('externalId')}")
                continue
            
            

            variable_type_entries = templateVariableTypeMap.get(template_id, [])

            unique_name_to_type = {
                list(entry.keys())[0]: list(entry.values())[0]
                for entry in variable_type_entries
            }

            for val in record.get('creativeTemplateVariableValues', []):
                asset_dict = val.get("asset")
                if asset_dict is not None:
                    val["type"] = "asset"
                    val["value"] = asset_dict.get("assetUrl")
                    continue

                unique_name = val.get("uniqueName")
                if unique_name and unique_name in unique_name_to_type:
                    val["type"] = unique_name_to_type.get(unique_name, "string")

        return super().validate_and_transform(preprocessed_records=preprocessed_records)
    