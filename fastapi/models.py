from datetime import datetime
from pydantic import BaseModel

class Tag(BaseModel):
    tag: str

class TagIn(BaseModel):
    tag: str

class TagOut(BaseModel):
    tag: str
    created: datetime