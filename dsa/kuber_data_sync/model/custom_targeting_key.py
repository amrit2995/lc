from pydantic import BaseModel, field_validator, ConfigDict, Field
from typing import Union
from enum import Enum
######### ENUMS ##############

class Type(Enum):
    FREEFORM = "FREEFORM"
    PREDEFINED = "PREDEFINED"

class Status(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNKNOWN = "UNKNOWN"

class ReportableType(Enum):
    CUSTOM_DIMENSION = "CUSTOM_DIMENSION"
    UNKNOWN = "UNKNOWN"
    OFF = "OFF"
    ON = "ON"

########## MODELS #############

class CustomeTargetingKey(BaseModel):

    externalId: str = Field(alias='id', serialization_alias="externalId")
    name: str
    displayName: Union[str, None] = ""
    type: dict
    status: dict
    reportableType: dict

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True
    )

    @field_validator("type", "status", "reportableType", mode='before')
    def to_dict(cls, value, values):

        enum = {
            "type": Type,
            "status": Status,
            "reportableType": ReportableType
        }

        return { "value": value } if value in enum[values.field_name].__members__ else None
    
    @field_validator("displayName", mode='before')
    def return_empty_string(cls, value, values):
        return value if value else ''