from enum import Enum
from delta_sdk.utils import logging

class EntityType(Enum):
    Advertiser = { "nucleus_key": "sync-advertisers", "dependencies": 1 }
    Order = { "nucleus_key": "sync-orders", "dependencies": 2 }
    Package = { "nucleus_key": "sync-packages", "dependencies": 1 }
    LineItem = { "nucleus_key": "sync-lineitems", "dependencies": 3 }
    Creative = { "nucleus_key": "sync-creatives", "dependencies": 3 }
    LineItemCreativeAssociation = { "dependencies": 5 }
    Label = { "nucleus_key": "sync-labels", "dependencies": 1 }
    CustomTargetingKey = { "nucleus_key": "sync-custom-targeting-keys", "dependencies": 1 }
    CustomTargetingValue = { "nucleus_key": "sync-custom-targeting-values", "dependencies": 2 }
    AdUnit = { "nucleus_key": "sync-ad-units", "dependencies": 1 }
    AudienceSegment = { "nucleus_key": "sync-audience-segments", "dependencies": 1 }
    CreativeTemplate = { "nucleus_key": "sync-creative-templates", "dependencies": 1 }
    Trafficker = { "nucleus_key": "sync-traffickers", "dependencies": 1 }
    Placement = { "nucleus_key": "sync-placements", "dependencies": 1 }
    GeoTarget = { "nucleus_key": "sync-geo-targets", "dependencies": 1 }
    BandwidthGroup = { "nucleus_key": "sync-bandwidth-groups", "dependencies": 1 }


    # def get_entities_from_nucleus(input_dict) -> list[str]: 
    #     entity_list = []
        
    #     for entity in EntityType:
    #         entity_data = entity.value
    #         nucleus_key = entity_data.get("nucleus_key")
            
    #         if nucleus_key and input_dict.get(nucleus_key, False):
    #             entity_list.append(entity.name)

    #     return entity_list
    
    # @staticmethod
    def get_entities_from_nucleus(entity_types_dict) -> list[str]:
        entity_list = []

        for entity in EntityType:
            entity_name = entity.name
            entity_settings = entity_types_dict.get(entity_name, {})

            if entity_settings.get("sync", False):
                entity_list.append(entity_name)

        return entity_list
    
    def configure_erase_before_insert(entity_config: dict, entity_class_map: dict):
        """
        Dynamically set ERASE_BEFORE_INSERT for each child entity class
        based on Nucleus configuration.
        
        Dynamically set filter for each child entity class
        based on Nucleus configuration.
        
        Dynamically set FULL_REFRESH_INTERVAL_IN_SECONDS for each child entity class
        based on Nucleus configuration.
        

        Args:
            entity_config (dict): The 'entityTypes' dictionary from Nucleus config
            entity_class_map (dict): Mapping of entity name to its class object
        """
        from kuber_data_sync.service.base import BaseEntity  # lazy import here

        for entity in EntityType:
            entity_name = entity.name
            config = entity_config.get(entity_name, {})
            erase_flag = config.get("eraseBeforeInsert", False)
            filter = config.get("filter", {})
            full_refresh_interval_in_seconds = config.get("fullRefreshIntervalInSeconds", 3600)
            if entity_name in entity_class_map:
                entity_class = entity_class_map[entity_name]
                if issubclass(entity_class, BaseEntity):
                    entity_class.ERASE_BEFORE_INSERT = erase_flag
                    entity_class.filter = filter
                    entity_class.FULL_REFRESH_INTERVAL_IN_SECONDS = full_refresh_interval_in_seconds
                    # logging.info(f"Set ERASE_BEFORE_INSERT={erase_flag} for {entity_name}")

            else:
                logging.warning(f"{entity_name} not found in entity_class_map")

class CommonConfigs:
    SYNC_MODE = 'REGULAR'
    TIMEZONE = 'UTC'
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    GC_INTERVAL = 120
    LAST_MODIFIED_DATA_SYNC_IN_HOURS = 24
    ENV = 'stage'
    
BASE_URLS = {
    'dev': 'https://internal-east4.carbon-dev.gcp.lowes.com',
    'stage': 'https://internal-east4.carbon-stage.gcp.lowes.com',
    'prod': 'https://internal-east4.carbon.gcp.lowes.com',
}

class HostConfigs:
    BASE_URL = BASE_URLS.get(CommonConfigs.ENV.lower())
    
    
class GAMConfigs:
    GAM_VERSION = 'v202408'

class MongoConfigs:
    CLUSTER_NAME = 'southdeep'
    DB_NAME = 'kuber'

class SyncMode:
    ALL = "ALL"
    REGULAR = 'REGULAR'


class ApiConfigs:
    BLUE_CREATIVE_ALL = {}
    BLUE_CREATIVE_REGULAR = {}

    @classmethod
    def load(cls, api_calls_config):
        cls.BLUE_CREATIVE_ALL = api_calls_config.get("blue-creative-all", cls.BLUE_CREATIVE_ALL)
        cls.BLUE_CREATIVE_REGULAR = api_calls_config.get("blue-creative-regular", cls.BLUE_CREATIVE_REGULAR)
    
    
