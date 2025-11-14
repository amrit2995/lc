from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum
from typing import Optional

################# ENUM ######################

class AssociationStatus(str, Enum): 
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

################# MODELS #####################

class LineItemCreativeAssociation(BaseModel):
    lineItemId: str
    creativeId: str
    associationStatus: AssociationStatus = Field(default=AssociationStatus.INACTIVE, alias="status", serialization_alias="associationStatus")

    model_config = ConfigDict(
        use_enum_values=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    # @field_validator('creativeId', 'lineItemId', mode='before')
    # @classmethod
    # def convert_to_string(cls, v):
    #     return str(v)
