from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Any, List

class BandwidthGroup(BaseModel):
    id: str = Field(alias='Id', serialization_alias='_id')
    bandwidthName: str = Field(alias='BandwidthName', serialization_alias='bandwidthName')
    
    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True,
        populate_by_name=True,
        extra='ignore'
    )