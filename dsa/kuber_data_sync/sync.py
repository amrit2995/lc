import requests
from delta_sdk.utils.nucleus import Nucleus
from delta_sdk.utils import logging
from delta_sdk.connectors.cloud.gcp.gam import GAMConnector
from delta_sdk.connectors.dao.mongo import MongoConnector
from kuber_data_sync.service.services import *
from kuber_data_sync.service.services import ENTITY_CLASS_MAP

from kuber_data_sync.configs import EntityType
from kuber_data_sync.configs import CommonConfigs, MongoConfigs, ApiConfigs, SyncMode, BASE_URLS
from kuber_data_sync.exceptions import ExceptionLogging
from kuber_data_sync.report import Report
from kuber_data_sync.periodic_gc import PeriodicGC
import json
import sys
import pytz
import threading
from datetime import datetime, time


def trigger_sync_from_nucleus(env, gam_nucleus_hash, kuber_config_hash, nucleus_hash):
    """Fetch entities from nucleus and then trigger sync.
    Args:
        env: Specify the env.
        gam_nucleus_hash: Used during GAM client creation via delta-sdk
        nucleus_hash: Used during Mongo client creation via delta-sdk
        kuber_config_hash: To fetch config from nucleus.
    """
    CommonConfigs.ENV = env
    if env == "dev":
        response = requests.get(
            f"{BASE_URLS[CommonConfigs.ENV]}/nucleus/config?applicationName=kuber&scope=gam-entity-data-sync",
            headers={
                'Authorization': kuber_config_hash,
                'Content-Type': 'application/json'
            }
        )
        config = response.json()["data"]
    else:
        config = Nucleus.get(
            env=env,
            nucleusHash=kuber_config_hash,
            applicationName='kuber',
            scope='gam-entity-data-sync'
        )['data']
    
    
    # with open("/Users/4670300/Documents/kuber-data-sync/nucleus_config.json", "r") as f:
    #     full_config = json.load(f)

    # config = full_config["data"]
    logging.info(f"Nucleus Configs for Sync :- {config}")
    # Extract fields
    entity_config = config.get("entity", {})
    persistence_config = config.get("persistence", {})
    recipients = config.get("recipients", [])
    ApiConfigs.load(config.get("api-calls", {}))

    # Set common configs
    CommonConfigs.SYNC_MODE = entity_config.get("syncMode", CommonConfigs.SYNC_MODE)
    CommonConfigs.TIMEZONE = config.get("timezone", CommonConfigs.TIMEZONE)
    CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS = entity_config.get("lastModifiedDataSyncInHours", CommonConfigs.LAST_MODIFIED_DATA_SYNC_IN_HOURS)
    MongoConfigs.CLUSTER_NAME = persistence_config.get("clusterName", MongoConfigs.CLUSTER_NAME)
    MongoConfigs.DB_NAME = persistence_config.get("dbName", MongoConfigs.DB_NAME)
    
    if recipients:
        Report.RECEPIENTS = recipients

    # Get entities to sync
    entity_types_config = entity_config.get("entityTypes", {})
    EntityType.configure_erase_before_insert(entity_config=entity_config.get("entityTypes", {}), entity_class_map=ENTITY_CLASS_MAP)
    entities = EntityType.get_entities_from_nucleus(entity_types_config)
    logging.info(f"Entities to sync: {entities}")
    return trigger_sync(env, gam_nucleus_hash=gam_nucleus_hash, nucleus_hash=nucleus_hash , entities=entities)

def trigger_sync(env: str, gam_nucleus_hash, nucleus_hash , entities: list[str]):
    """Trigger syncs for the 'entities' provided.
    Args::
        env:
        gam_nucleus_hash: Used during GAM client creation via delta-sdk
        nucleus_hash: Used during Mongo client creation via delta-sdk
        entities : list of entities for whom entity must be synched.

    Note::
        Sync entities one by one that are provided in the 'entities' list.
    """
    # periodic_gc = PeriodicGC().start()
    try:
        Report.start()
        gam_client = GAMConnector(env=env, nucleusHash=gam_nucleus_hash).get_client()
        mongo_client = MongoConnector(env=env, nucleusHash=nucleus_hash, clusterName=MongoConfigs.CLUSTER_NAME).client
        # for local use
        # import pymongo;mongo_client = pymongo.MongoClient(host="mongodb://localhost:27017")

        if not (gam_client and mongo_client):
            raise RuntimeError(f"GAM and Mongo Clients are necessary. Either of the Cient Creations failed.")
        
        if {"Advertiser", "Order"}.issubset(set(entities)): entities.append("Package")
        if {"LineItem", "Creative"}.issubset(set(entities)): entities.append("LineItemCreativeAssociation")
        entities = [entity.name for entity in sorted(EntityType, key=lambda e: e.value['dependencies']) if entity.name in set(entities)]
        logging.info(f"Following entities were synched successfully :- {', '.join(entities)}")
        # For Treating String Objects as Global Classes
        entity_service_classes  = [globals()[entity] for entity in entities]
        synched_entities = set()
        for entity_service in entity_service_classes:
            logging.info(f"{entity_service.__name__}, SYNC MODE = {CommonConfigs.SYNC_MODE} , ERASE_BEFORE_INSERT = {entity_service.ERASE_BEFORE_INSERT}, FILTER_QUERY = {entity_service.filter}, FULL_REFRESH_INTERVAL_IN_SECONDS = {entity_service.FULL_REFRESH_INTERVAL_IN_SECONDS}")
            sync_successful = entity_service.sync(mongo_client=mongo_client, gam_client=gam_client, synched_entities=synched_entities)
            if sync_successful: synched_entities.add(entity_service.__name__)
            
        logging.info(f"Following entities were synched successfully :- {', '.join(synched_entities)}")
        # Sync Blue Creatives Method if Creative was synced
        if "Creative" in synched_entities:
            sync_blue_creatives(cls=Creative, mongo_client=mongo_client)
            
        logging.info("Final report notification.")
        # Report.send_postie_email(env=env)
    
    except Exception as e:
        exception_log = f"{type(e).__name__}:{e}"
        logging.error(exception_log)
        ExceptionLogging.log_error(mongo_client=mongo_client, exceptionType=type(e).__name__, error_log=e)
        # Report.send_failure_alert(env=env, exception_log=exception_log)
    # finally:
    #     periodic_gc.cancel()
    
def sync_blue_creatives(cls, mongo_client):
    logging.info("Starting sync method for blue creatives.")

    config = (
        ApiConfigs.BLUE_CREATIVE_ALL
        if CommonConfigs.SYNC_MODE == SyncMode.ALL
        else ApiConfigs.BLUE_CREATIVE_REGULAR
    )

    if not config.get("active"):
        return True

    method = config.get("method", "GET").upper()
    url = config.get("url")
    headers = config.get("headers", {})

    if method == "GET":
        threading.Thread(
            target=requests.get,
            args=(url,),
            kwargs={"headers": headers},
            daemon=True
        ).start()

    elif method == "POST":
        target_tz = pytz.timezone(CommonConfigs.TIMEZONE)
        current_date_utc = target_tz.localize(
            datetime.combine(datetime.now(target_tz).date(), time.min)
        )

        projection = {"externalId": 1, "_id": 0}
        query_filter = {"lastRefreshDateTime": {"$gte": current_date_utc}}
        creative_records = mongo_client[MongoConfigs.DB_NAME][cls.mongo_collection_name].find(
            query_filter, projection=projection
        )

        creative_ids = [str(record['externalId']) for record in creative_records if 'externalId' in record]
        payload = {"creativeIds": creative_ids}

        threading.Thread(
            target=requests.post,
            args=(url,),
            kwargs={"headers": headers, "json": payload},
            daemon=True
        ).start()

    else:
        logging.warning(f"Unsupported HTTP method: {method}")

    return True
