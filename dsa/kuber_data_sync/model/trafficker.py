from pydantic import BaseModel, Field, ConfigDict
from typing import Union, Optional

class Trafficker(BaseModel):
    id: str = Field(alias='id', serialization_alias="_id")
    name: str
    email: Optional[str] = Field(default="")
    roleId: str
    roleName: str
    isActive: bool
    isServiceAccount: bool

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True,
        populate_by_name=True
    )

    def model_post_init(self, __context):
        # Force email to always be "N/A"
        self.email = ""
