from kuber_data_sync.service.base import BaseEntity
from dataclasses import dataclass, asdict
from kuber_data_sync.configs import MongoConfigs
import bson
import pymongo
from delta_sdk.utils import logging
from enum import Enum
from typing import Union

__all__ = ["Package"]


##################### ENUMS #####################

class AdType(Enum):
    DISPLAY = 'DISPLAY'

class AdSubtype(Enum):
    PMP = "PMP"

class Status(Enum):
    ACTIVE = "ACTIVE"

##################### ENUMS #####################
@dataclass
class PackageSchema:
    name: str
    adType: str = AdType.DISPLAY.value
    adSubtype: str = AdSubtype.PMP.value
    adServer: str= "Google Ad Manager"
    orderId: Union[bson.ObjectId, None] = None
    advertiserId: Union[bson.ObjectId, None] = None
    packageEntityStatus: str = Status.ACTIVE.value


class Package(BaseEntity):

    mongo_collection_name = "package"
    packages = []

    @classmethod
    def create(cls, name, orderId, advertiserId):
        package = asdict(PackageSchema(
            name=name,
            orderId=orderId,
            advertiserId=advertiserId
        ))

        logging.info(f"Creating new pacakge: {package}")
        cls.packages.append(package)
        
    
    @classmethod
    def mongo_create_dump(cls, mongo_client: pymongo.MongoClient):
        logging.info("Dumping packages to mongo (upsert mode)")


        if cls.packages:
            logging.info("Upserting created packages.")

            collection = mongo_client[MongoConfigs.DB_NAME][cls.mongo_collection_name]
            bulk_operations = []

            for record in cls.packages:
                bulk_operations.append(
                    pymongo.UpdateOne(
                        {"orderId": record["orderId"]},
                        {"$set": record},
                        upsert=True
                    )
                )
            
            if bulk_operations:
                result = collection.bulk_write(bulk_operations).bulk_api_result
                logging.info(f"Bulk upsert result: {result}")
            else:
                logging.info("No operations to perform in bulk upsert.")
        else:
            logging.info("No new created Packages to upsert.")

        cls.packages = []

            