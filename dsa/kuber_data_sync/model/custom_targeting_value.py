from pydantic import BaseModel, field_validator, ConfigDict, Field
from enum import Enum


##################### ENUM #########################

class MatchType(Enum):
    BROAD = 'BROAD'
    BROAD_PREFIX = 'BROAD_PREFIX'
    EXACT = 'EXACT'
    PREFIX = 'PREFIX'
    SUFFIX = 'SUFFIX'
    CONTAINS = 'CONTAINS'
    UNKNOWN = 'UNKNOWN'

class Status(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    UNKNOWN = 'UNKNOWN'

####################### MODELS ######################

class CustomTargetingValue(BaseModel):
    customTargetingKeyId: str
    externalId: str = Field(alias='id', serialization_alias="externalId")
    name: str
    displayName: str = ''
    status: dict
    matchType: dict

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True
    )

    @field_validator("displayName", mode="before")
    def check_display_name(cls, value):
        return value if value else ''
    
    @field_validator("matchType", "status", mode='before')
    def to_dict(cls, value, values):

        enum = {
            "matchType": MatchType,
            "status": Status
        }

        return { "value": value } if value in enum[values.field_name].__members__ else None