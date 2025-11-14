from pydantic import BaseModel, field_validator, ConfigDict, Field, model_validator, computed_field
from typing import Optional
from pydantic_extra_types.color import Color
from enum import Enum
from typing import Union
from kuber_data_sync.model.time import DateTime
from datetime import datetime
from bson import ObjectId

############## Enums ##############

class CreativeStatus(Enum):
    CREATIVES_APPROVED = "CREATIVES_APPROVED"
    NEEDS_CREATIVES = "NEEDS_CREATIVES"

class AdvertisementType(Enum):
    DISPLAY = "DISPLAY"
    SPONSORED = "SPONSORED"
    
class DeliveryType(Enum):
    ALL_CREATIVES = "ALL_CREATIVES"
    GREATER_THAN_ONE_CREATIVE = "GREATER_THAN_ONE_CREATIVE"
    ONE_CREATIVE = "ONE_CREATIVE"

RoadBlockingTypeToDeliveryTypeMap = {
    "ONLY_ONE" : "ONE_CREATIVE",
    "ONE_OR_MORE" : "GREATER_THAN_ONE_CREATIVE",
    "ALL_ROADBLOCK" : "ALL_CREATIVES"
}

DeliveryRateType2PacingTypeMapping = {
    "AS_FAST_AS_POSSIBLE":"FAST",
    "FRONTLOADED":"FRONTLOADED",
    "EVENLY":"EVEN"
}

class TimeZone(Enum):
    BROWSER = "BROWSER"
    PUBLISHER = "PUBLISHER"

class LogicalOperator(Enum):
    OR = "OR"
    AND = "AND"
    
class ConditionOperator(Enum):
    IS = "IS"
    IS_NOT = "IS_NOT"
    
def return_line_item_status(status_value: str) -> str:
    if status_value == "DRAFT":
        return "RESERVED"
    elif status_value in {"INACTIVE", "DELIVERING", "DELIVERY_EXTENDED", "READY"}:
        return "RESERVED_AND_READY"
    elif status_value in {"PAUSED_INVENTORY_RELEASED", "PAUSED"}:
        return "PAUSED"
    elif status_value == "COMPLETED":
        return "COMPLETED"
    elif status_value == "DISAPPROVED":
        return "REJECTED"
    elif status_value == "CANCELED":
        return "ARCHIVED"
    else:
        return "DRAFT"

############## MODELS #############

class Pricing(BaseModel):

    pricingModel: str
    pricingValue: float
    budget: float
    quantity: int

class Size(BaseModel):
    width: int
    height: int
    isAspectRatio : Optional[bool]
    
class CreativeSizes(BaseModel):
    height: Optional[str] = ""
    width: Optional[str] = ""
    sizeType: Optional[str] = Field(default="", alias="creativeSizeType", serialization_alias="sizeType")
    creativeTemplateId: Optional[str] = ""

    @field_validator("height", "width", mode="before")
    def to_str(cls, v):
        return str(v)

    @field_validator("creativeTemplateId", mode="before")
    def template_id_to_str(cls, v):
        return str(v) if v is not None else ""
    # companions: list
    # appliedLabels: list
    # effectiveAppliedLabels: list
    # expectedCreativeCount: int
    # creativeSizeType: str
    # targetingName: Union[str, None]
    # isAmpOnly: bool

    # model_config = ConfigDict(
    #     coerce_numbers_to_str=True
    # )

class FrequencyCap(BaseModel):
    numberOfTimeUnit: int = Field(alias="numberOfTimeUnit", serialization_alias="numTimeUnits")
    timePeriod: int = Field(alias="timePeriod", serialization_alias="timeUnit")
    impression: int = Field(alias="impression", serialization_alias="maxImpressions")

class TimeVal(BaseModel):
    hour: int
    minute: Union[int, str]  # To support values like "ZERO", "FIFTEEN"

class TimeSlot(BaseModel):
    from_time: TimeVal = Field(alias="from")
    to_time: TimeVal = Field(alias="to")
    dayOfWeek: str

class DayPartingTargetting(BaseModel):
    timeZone: TimeZone = Field(default=None)
    dayParts: list[TimeSlot] = Field(default_factory=list, alias="timeSlots")
    timeSlots: list[TimeSlot] = Field(default_factory=list)

    model_config = ConfigDict(
        use_enum_values=True
    )

class Condition(BaseModel):
    keyId: Optional[str] = None
    valueIds: Optional[list[str]] = None
    operator: ConditionOperator
    # audienceSegmentIds: Optional[list[str]] = None

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

    @field_validator("valueIds", mode="before")
    def convert_2_str(cls, value, values):
        if isinstance(value, list):
            return [ str(ele) for ele in value ]
        return []

class LogicalCondition(BaseModel):
    logicalOperator: LogicalOperator
    children: list["LogicalCondition", Condition]

class CustomTargeting(BaseModel):
    keyId: str
    operator: str
    valueId: list = Field(alias='valueIds', serialization_alias="valueId")

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

    @field_validator("valueId", mode="before")
    def to_string_list(cls, value, values):
        return [str(ele) for ele in value]

class BandwidthGroup(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

class BandwidthGroupTargeting(BaseModel):
    bandwidthGroups: list[BandwidthGroup] = Field(default=[])

class TechnologyTargetting(BaseModel):
    isTargeted: bool = Field(default=True) 
    bandwidthGroupTargeting: Union[BandwidthGroupTargeting, None]

class UserDomainTargeting(BaseModel):
    targeted: bool = Field(default=True)
    domains: list[str]

class GeoLocation(BaseModel):
    displayName: str
    parentId: Optional[int] = Field(alias="canonicalParentId", serialization_alias="parentId")
    id: Optional[int] = Field(alias="_id", serialization_alias="id")
    type: str

    model_config = ConfigDict(
        populate_by_name=True,       
        coerce_numbers_to_str=False
    )

class GeoTargetting(BaseModel):
    targetedLocations : list[GeoLocation]
    excludedLocations : list[GeoLocation]

class AdUnitTarget(BaseModel):
    unitId: str = Field(alias='adUnitId', serialization_alias="unitId")
    # includeDescendants: Optional[bool] = Field(alias='includeDescendants', serialization_alias="includeDescendants")

class InventoryTargeting(BaseModel):
    adUnitTarget: list[AdUnitTarget] = Field(alias="targetedAdUnits", serialization_alias='adUnitTarget', default=[])
    excludedAdUnitTarget: list[AdUnitTarget] = Field(alias="excludedAdUnits", serialization_alias='excludedAdUnitTarget', default=[])
    # targetedPlacementIds: list[AdUnitTarget] = Field(default=[])

class Targeting(BaseModel):
    adUnit: Union[InventoryTargeting, None] = Field(alias="inventoryTargeting", serialization_alias="adUnit", default={})
    frequencyCap: Union[list[FrequencyCap], None] = Field(alias="frequencyCaps", serialization_alias="frequencyCap", default=[])
    dayParting: Union[DayPartingTargetting, None] = Field(alias="dayPartTargeting", serialization_alias="dayParting", default={})
    custom: Union[any] = Field(alias="customTargeting", serialization_alias="custom", default=[])
    technologyTargeting: Union[TechnologyTargetting, None] = Field(alias="technologyTargeting", serialization_alias="technologyTargeting", default={})
    userDomainTargeting: Union[UserDomainTargeting, None] = Field(alias="userDomainTargeting", serialization_alias="userDomainTargeting", default={})
    geoTargeting: Union[GeoTargetting, None] = Field(alias="geoTargeting", serialization_alias="geoTargeting", default={})

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    @field_validator("custom", mode='before')
    def custom_targeting(cls, value, values):
        if not value:
            return []
        or_value = value
        new_or_value = []
        if or_value.get('logicalOperator') == LogicalOperator.OR.value:
            and_values = or_value.get('children')
            new_and_values = []
            for and_value in and_values:
                if and_value.get('logicalOperator') == LogicalOperator.AND.value:
                    is_values = and_value.get('children')
                    new_is_values = []
                    for is_value in is_values:
                        if (is_value.get('valueIds') and is_value.get('keyId')):
                            new_is_values.append(CustomTargeting(**is_value).model_dump())
                    new_and_values.append(new_is_values)
            new_or_value = new_and_values
        return new_or_value

    @field_validator("geoTargeting", mode="before")
    def fix_geo_targeting_empty_list(cls, value):
        # Convert [] → None to avoid Pydantic warning
        return None if value == [] else value

    @field_validator("frequencyCap", mode="after")
    def fix_frequency_cap_empty(cls, value):
        return value if value else []


class LineItem(BaseModel):
    externalId: str = Field(alias='id', serialization_alias="externalId")
    name : str
    orderId: Optional[Union[ObjectId, str, int]] = None
    advertiserId: Optional[Union[ObjectId, str, int]] = None
    packageId: Optional[Union[ObjectId, str, int]] = None
    priorityValue: int = Field(alias='priority', serialization_alias='priorityValue')
    creativeStatus: CreativeStatus = Field(alias='status', serialization_alias='creativeStatus')
    advertisementType: AdvertisementType = AdvertisementType.DISPLAY.value
    delivery: dict = Field(alias='roadblockingType', serialization_alias='delivery', default=RoadBlockingTypeToDeliveryTypeMap["ALL_ROADBLOCK"])
    primaryGoal: dict
    costType: str
    costPerUnit: dict
    pacingType: str = Field(alias='deliveryRateType', serialization_alias='pacingType')
    type: str = Field(alias='lineItemType', serialization_alias='type')
    status: str = Field(alias='status', serialization_alias='status')
    allowOverBooking: Optional[bool] = Field(alias="allowOverbook", serialization_alias="allowOverBooking", default=False)
    creativeSizes: list[CreativeSizes] = Field(alias="creativePlaceholders", serialization_alias="creativeSizes", default=[])
    targeting: Targeting
    startTime: Union[datetime, None] = Field(alias='startDateTime', serialization_alias="startTime", default=None)
    endTime: Union[datetime, None] = Field(alias='endDateTime', serialization_alias="endTime", default=None)
    createTime: Union[datetime, None] = Field(alias='creationDateTime', serialization_alias='createTime', default=None)
    updateTime: Union[datetime, None] = Field(alias='lastModifiedDateTime', serialization_alias='updateTime', default=None)

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True,
        arbitrary_types_allowed=True
    )
    
    @model_validator(mode='before')
    @classmethod
    def override_status_if_archived(cls, data: dict) -> dict:
        if data.get("isArchived") is True:
            data["status"] = "ARCHIVED"
        return data
    
    @field_validator("status", mode="before")
    def map_status(cls, value):
        return return_line_item_status(value)
    
    @field_validator("creativeSizes", mode="before")
    def flatten_creative_sizes(cls, values: list[dict[str, any]]):
        result = []
        for item in values:
            size = item.get("size", {})
            flattened = {
                "width": size.get("width"),
                "height": size.get("height"),
                "creativeSizeType": item.get("creativeSizeType"),
                "creativeTemplateId": item.get("creativeTemplateId")
            }
            result.append(flattened)
        return result
    
    @computed_field(return_type=Pricing)
    @property
    def pricing(self):

        micro_amount = self.costPerUnit.get('microAmount')
        quantity = self.primaryGoal.get("units", 1)
        pricing_model = self.costType

        try:
            pricing_value = float(((micro_amount / 1_000_000.0) * 1000) / quantity)
            budget = float(micro_amount / 1_000_000.0)
        except (TypeError, ZeroDivisionError):
            pricing_value = 0.0
            budget = 0.0

        return Pricing(
            pricingModel=pricing_model,
            pricingValue=pricing_value,
            budget=budget,
            quantity=quantity
        )

    @field_validator("createTime", "updateTime", "startTime", "endTime", mode='before')
    def zeep_2_dt_obj(cls, value, values):
        if value:
            return DateTime(**value).date_time_object
        return None
    
    @field_validator("creativeStatus", mode='before')
    def creative_status(cls, value, values):
        return CreativeStatus.CREATIVES_APPROVED if value else CreativeStatus.NEEDS_CREATIVES
    
    @field_validator("delivery", mode='before')
    def roadblocking_2_delivery_type_map(cls, value, values):
        return {
            "deliveryType": RoadBlockingTypeToDeliveryTypeMap.get(value, RoadBlockingTypeToDeliveryTypeMap["ALL_ROADBLOCK"])
        }

    @field_validator("pacingType", mode="before")
    def delivery_rate_type_2_pacing_type(cls, value, values):
        return DeliveryRateType2PacingTypeMapping.get(value, DeliveryRateType2PacingTypeMapping['EVENLY'])