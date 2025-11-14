from pydantic import BaseModel, field_validator, ConfigDict, Field
from typing import Optional
from pydantic_extra_types.color import Color
from enum import Enum
from typing import Union
from kuber_data_sync.model.time import DateTime
from datetime import datetime

############## Enums ##############

class Type(Enum):
    COMPETITIVE_EXCLUSION = 'COMPETITIVE_EXCLUSION'
    AD_EXCLUSION = 'AD_EXCLUSION'
    AD_UNIT_FREQUENCY_CAP = 'AD_UNIT_FREQUENCY_CAP'
    CREATIVE_WRAPPER = 'CREATIVE_WRAPPER'
    CANONICAL_CATEGORY = 'CANONICAL_CATEGORY'
    UNKNOWN = 'UNKNOWN'

############## MODELS #############

class Label(BaseModel):
    id: str = Field(alias='id', serialization_alias='_id')
    name: str
    description: Union[str, None]
    isActive: bool
    adCategory: Union[str, None] = None
    types: list[Type]

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True
    )
