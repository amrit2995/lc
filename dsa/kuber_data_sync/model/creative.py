from pydantic import BaseModel, Field, field_validator, ConfigDict, AnyUrl
from enum import Enum
from kuber_data_sync.model.time import DateTime
from datetime import datetime
from bson import ObjectId
from typing import Union, Optional, Literal

##################### ENUMS ####################

class SizeType(Enum):
    NATIVE = 'NATIVE'

class CreativeType(Enum):
    NATIVE = "NATIVE"

class Status(Enum):
    READY = "READY"

class CreativePolicyViolation(Enum):
    MALWARE_IN_CREATIVE = "MALWARE_IN_CREATIVE"
    MALWARE_IN_LANDING_PAGE = "MALWARE_IN_LANDING_PAGE"
    LEGALLY_BLOCKED_REDIRECT_URL = "LEGALLY_BLOCKED_REDIRECT_URL"
    MISREPRESENTATION_OF_PRODUCT = "MISREPRESENTATION_OF_PRODUCT"
    SELF_CLICKING_CREATIVE = "SELF_CLICKING_CREATIVE"
    GAMING_GOOGLE_NETWORK = "GAMING_GOOGLE_NETWORK"
    DYNAMIC_DNS = "DYNAMIC_DNS"
    CIRCUMVENTING_SYSTEMS = "CIRCUMVENTING_SYSTEMS"
    PHISHING = "PHISHING"
    DOWNLOAD_PROMPT_IN_CREATIVE = "DOWNLOAD_PROMPT_IN_CREATIVE"
    UNAUTHORIZED_COOKIE_DETECTED = "UNAUTHORIZED_COOKIE_DETECTED"
    TEMPORARY_PAUSE_FOR_VENDOR_INVESTIGATION = "TEMPORARY_PAUSE_FOR_VENDOR_INVESTIGATION"
    ABUSIVE_EXPERIENCE = "ABUSIVE_EXPERIENCE"
    TRICK_TO_CLICK = "TRICK_TO_CLICK"
    USE_OF_NON_ALLOWLISTED_OMID_VERIFICATION_SCRIPT = "USE_OF_NON_ALLOWLISTED_OMID_VERIFICATION_SCRIPT"
    MISUSE_OF_OMID_API = "MISUSE_OF_OMID_API"
    UNACCEPTABLE_HTML_AD = "UNACCEPTABLE_HTML_AD"
    UNKNOWN = "UNKNOWN"

##################### MODELS ###################

class Size(BaseModel):
    width: str
    height: str
    sizeType: Optional[SizeType] = SizeType.NATIVE.value

    model_config = ConfigDict(
        coerce_numbers_to_str=True,
        use_enum_values=True
    )


class CreativeTemplateValue(BaseModel):
    uniqueName: str
    value: Optional[Union[str, int, float, dict]] = Field(default=None)
    type: Literal["asset", "long", "string", "url", "listString"]

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        strict=True
    )

class AppliedLabel(BaseModel):
    labelId: str
    isNegated: bool

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

class Creative(BaseModel):

    externalId: str = Field(alias="id", serialization_alias="externalId")
    name: str
    advertiserId: Union[ObjectId, str]
    destinationUrl: Union[str, any] = None
    templateId: str = Field(alias='creativeTemplateId', serialization_alias="templateId", default=None)
    creativeSize: Size = Field(alias="size", serialization_alias="creativeSize", default=None)
    templateValues: Union[list[CreativeTemplateValue], None] = Field(alias='creativeTemplateVariableValues', serialization_alias='templateValues', default=[])
    # previewUrl: str
    policyLabels: Union[CreativePolicyViolation, any] = None
    creativeType: str = Field(default="NATIVE")
    status: Status = Status.READY.value
    updateTime: datetime = Field(alias='lastModifiedDateTime', serialization_alias='updateTime')
    appliedLabelsCreative: Union[list[AppliedLabel], None] = Field(alias='appliedLabels', serialization_alias="appliedLabelsCreative", default=None)
    adBadgingEnabled: bool

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True,
        arbitrary_types_allowed=True
    )
    
    def model_post_init(self, __context):
        # Force creativeType to always be "NATIVE"
        self.creativeType = "NATIVE"

    @field_validator("updateTime", mode='before')
    def zeep_2_dt_obj(cls, value, values):
        return DateTime(**value).date_time_object