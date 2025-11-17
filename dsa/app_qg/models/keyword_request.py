from pydantic import BaseModel,validator
from typing import  List

class KeywordRequest(BaseModel):
    searchTerms: List[str]
    omniItemIds: List[str]
    spellCheck: bool = False


    @validator('searchTerms')
    def check_non_empty(cls, v):
        if len(v) < 1:
            raise ValueError('Search terms must contain at least one searchTerm')
        elif len(v) > 100:
            raise ValueError('Search terms cannot cannot contain more than 100 searchTerms')
        return v
    
    @validator('omniItemIds')
    def check_productId_non_empty(cls, v):
        if len(v) < 1:
            raise ValueError('OmniItemIds must contain at least one OmniItemId')
        elif len(v) > 100:
            raise ValueError('OmniItemIds cannot cannot contain more than 100 OmniItemIds')
        return v