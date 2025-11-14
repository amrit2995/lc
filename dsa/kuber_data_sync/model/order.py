from pydantic import BaseModel, field_validator, ConfigDict, Field
from typing import Optional, Union
from pydantic_extra_types.color import Color
from enum import Enum
from typing import Union
import bson
from kuber_data_sync.model.time import DateTime
from datetime import datetime

############## Enums ##############


def get_order_status(item):
    if item["status"] in ["DRAFT", "PENDING_APPROVAL", "APPROVED", "DISAPPROVED"]:
        return "RESERVED"
    elif item["status"] == "DELETED":
        return "ARCHIVED"
    else:
        return item["status"]
    
class PacingType(Enum):
    EVEN = 'EVEN'
    FAST = 'FAST'
    FRONTLOADED = 'FRONTLOADED'

class OrderType(Enum):
    DISPLAY = 'DISPLAY'
    # SPONSORED = 'SPONSORED'

############## MODELS #############

class Order(BaseModel):
    externalId: str = Field(alias='id', serialization_alias='externalId')
    name : str
    orderType: str = Field(default="DISPLAY")
    status: str
    traffickerId: str
    advertiserId: bson.ObjectId
    updateTime: datetime = Field(alias="lastModifiedDateTime", serialization_alias='updateTime')
    # appliedLabels: Union[list[str], None] = None

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True,
        arbitrary_types_allowed=True
    )
    
    @field_validator("status", mode='before')
    def map_status(cls, value):
        # Map the status using the custom logic
        item = {"status": value}
        return get_order_status(item)


    @field_validator("updateTime", mode='before')
    def zeep_2_dt_obj(cls, value, values):
        return DateTime(**value).date_time_object
    
    def model_post_init(self, __context):
        # Force orderType to always be "DISPLAY"
        self.orderType = "DISPLAY"

