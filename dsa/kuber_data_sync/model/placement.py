from pydantic import BaseModel, field_validator, ConfigDict, Field
from typing import Optional
from enum import Enum
from typing import Union
from kuber_data_sync.model.time import DateTime
from datetime import datetime

#################### ENUMS #####################
class Status(Enum): 
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"

#################### MODELS ####################

class Placement(BaseModel):
    externalId: str = Field(alias='id', serialization_alias="externalId")
    name : str
    description: Union[str, None] = None
    placementCode: str
    status: Status
    targetedAdUnitIds: list[str]
    createTime: Optional[datetime] = None
    #Doubt: Where do we get this from? 
    updateTime: datetime = Field(alias="lastModifiedDateTime", serialization_alias="updateTime")

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True
    )

    @field_validator("createTime", "updateTime", mode='before')
    def zeep_2_dt_obj(cls, value, values):
        return DateTime(**value).date_time_object

    
