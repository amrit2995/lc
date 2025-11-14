from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing import Optional, Union, List, Literal


class Choice(BaseModel):
    label: str
    value: str


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class Type(str, Enum):
    SYSTEM_DEFINED = "SYSTEM_DEFINED"
    USER_DEFINED = "USER_DEFINED"

class MimeTypeValue(BaseModel):
    value: str

class Variable(BaseModel):
    label: str
    uniqueName: str
    description: Optional[str]
    isRequired: bool
    defaultValue: Optional[Union[str, int, float]] = None
    isTrackingUrl: Optional[bool] = False
    allowOtherChoice: bool = False
    choices: Optional[List[Choice]] = None
    mimeTypes: Optional[List[MimeTypeValue]] = None
    type: Literal["asset", "long", "string", "url", "listString"]

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        strict=True
    )


class CreativeTemplate(BaseModel):
    id: str = Field(alias='id', serialization_alias='_id')
    name: str
    description: Optional[str] = None
    status: dict
    type: dict
    variables: List[Variable]
    snippet: str
    isInterstitial: bool = False
    isNativeEligible: bool = False
    isSafeFrameCompatible: bool = False

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True
    )

    @field_validator("type", "status", mode='before')
    def to_enum_dict(cls, value, values):
        enums = {
            "type": Type,
            "status": Status
        }
        if value in enums[values.field_name].__members__:
            return {"value": value}
        if value in [e.value for e in enums[values.field_name]]:
            return {"value": value}
        return None
