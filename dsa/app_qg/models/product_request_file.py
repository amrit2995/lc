from pydantic import BaseModel,HttpUrl,validator,confloat
from typing import  List,Optional

class ProductRequestFile(BaseModel):
    omniItemIds: List[str]
    increaseCoverage: bool = False
    qgenMinScore: confloat(ge=0.0, lt=10.0) = 0.0
    qgenMaxScore: confloat(ge=0.0, le=10.0) = 10.0
    webhookUrl: Optional[HttpUrl] = None


    @validator('omniItemIds')
    def check_non_empty(cls, v):
        if len(v) < 1:
            raise ValueError('OmnitemIds must contain at least one omniItemId')
        elif len(v) > 100000:
            raise ValueError('OmnitemIds cannot cannot contain more than 100000 omniItemIds')
        return v
    