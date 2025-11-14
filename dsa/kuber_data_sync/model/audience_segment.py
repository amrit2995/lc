from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum
from typing import Union

##################### ENUMS ####################

class Status(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNUSED = "UNUSED"
    UNKNOWN = "UNKNOWN"

class Type(Enum):
    FIRST_PARTY = "FIRST_PARTY"
    SHARED = "SHARED"
    THIRD_PARTY = "THIRD_PARTY"
    UNKNOWN = "UNKNOWN"

##################### MODELS ###################

class DataProvider(BaseModel):
    name: str

class AudienceSegment(BaseModel):
    id: str = Field(alias="id", serialization_alias="_id")
    name: str
    categoryIds: list[str]
    description: Union[str, None]
    status: Status
    size: str
    mobileWebSize: str
    idfaSize: str
    adIdSize: str
    ppidSize: str
    dataProvider: DataProvider
    type: Type

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True ,
        populate_by_name = True #specifically done alias = True because _id is used in and pydantuc don't allow that.
    )

    @field_validator("description", mode="before")
    def empty_str_for_null(cls, value, values):
        return '' if not value else value