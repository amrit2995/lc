from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Any, List

class GeoTarget(BaseModel):
    id: int = Field(alias='Id', serialization_alias='_id')
    name: str = Field(alias='Name', serialization_alias='name')
    countryCode: str = Field(alias='CountryCode', serialization_alias='countryCode')
    canonicalParentId: Optional[object] = Field(default=None, alias='CanonicalParentId', serialization_alias='canonicalParentId')
    parentIds: Optional[List[str]] = Field(default=None, alias='ParentIds', serialization_alias='parentIds')

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True,
        populate_by_name=True,
        extra='ignore'
    )
    
    @field_validator('parentIds', mode='before')
    @classmethod
    def split_comma_separated(cls, v):
        if v is None:
            return None

        # Case 1: already a proper list of strings
        if isinstance(v, list):
            if len(v) == 1 and isinstance(v[0], str) and "," in v[0]:
                return [s.strip() for s in v[0].split(",")]
            elif all(isinstance(i, str) for i in v):
                return v
            else:
                raise TypeError("parentIds must be a list of strings")

        # Case 2: single comma-separated string
        if isinstance(v, str):
            return [s.strip() for s in v.split(",")]

        raise TypeError("parentIds must be a list or comma-separated string")
