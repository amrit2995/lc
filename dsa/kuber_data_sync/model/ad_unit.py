from pydantic import BaseModel, field_validator, ConfigDict, Field
from typing import Optional
from pydantic_extra_types.color import Color
from enum import Enum
from typing import Union
from kuber_data_sync.model.time import DateTime
from datetime import datetime

######### Enums ##############

class Status(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"

class EnvType(Enum):
    BROWSER = "BROWSER"
    APP = "APP"
    VIDEO_PLAYER = "VIDEO_PLAYER"

class AdType(Enum):
    TEXT_AND_IMAGE = "TEXT_AND_IMAGE"

class BorderStyle(Enum):
    DEFAULT = "DEFAULT"
    NOT_ROUNDED = "NOT_ROUNDED"
    SLIGHTLY_ROUNDED = "SLIGHTLY_ROUNDED"
    VERY_ROUNDED = "VERY_ROUNDED"

class FontSize(Enum):
    DEFAULT = "DEFAULT"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

class AdsensingSettingsSource(Enum):
    DIRECTLY_SPECIFIED = "DIRECTLY_SPECIFIED"
    PARENT = "PARENT"

class SmartSizeMode(Enum):
    NONE = "NONE"
    SMART_BANNER = "SMART_BANNER"
    UNKNOWN = "UNKNOWN"
    DYNAMIC_SIZE = "DYNAMIC_SIZE"

class TargetWindow(Enum):
    TOP = "TOP"
    BLANK = "BLANK"

class FontFamily(Enum):
    DEFAULT = "DEFAULT"
    ARIAL = "ARIAL"
    TAHOMA = "TAHOMA"
    GEORGIA = "GEORGIA"
    TIMES = "TIMES"
    VERDANA = "VERDANA"
    
class TimeUnit(Enum):
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    LIFETIME = "LIFETIME"
    POD = "POD"
    STREAM = "STREAM"
    UNKNOWN = "UNKNOWN"

########### MODELS #############

class AdUnitParentPath(BaseModel):
    id: str = Field(alias="_id", serialization_alias="_id")
    name: str
    adUnitCode: str

    model_config = ConfigDict(
        populate_by_name=True
    )

class AdUnitSizeDimensions(BaseModel):
    width: int
    height: int
    isAspectRatio: bool

class AdUnitSize(BaseModel):
    size: AdUnitSizeDimensions
    environmentType: EnvType
    fullDisplayString: str
    isAudio: bool

    model_config = ConfigDict(
        use_enum_values=True
    )

class AdSensingSettings(BaseModel):
    adSenseEnabled: bool
    borderColor: Union[Color, None]
    titleColor: Union[Color, None]
    backgroundColor: Union[Color, None]
    textColor: Union[Color, None]
    urlColor: Union[Color, None]
    adType: Optional[AdType]
    borderStyle: Union[BorderStyle, None]
    fontSize: Union[FontSize, None]
    fontFamily: Union[FontFamily, None]

class FrequencyCap(BaseModel):
    maxImpressions: str
    numTimeUnits: str
    timeUnit: TimeUnit

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

class LabelFrequencyCap(BaseModel):
    frequencyCap: FrequencyCap
    labelId: str

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

class AppliedLabel(BaseModel):
    labelId: str
    isNegated: bool

    model_config = ConfigDict(
        coerce_numbers_to_str=True
    )

class AdUnit(BaseModel):

    externalId: str = Field(alias='id', serialization_alias="externalId")
    parentId: Union[str, None]
    hasChildren: bool
    parentPath: Union[list[AdUnitParentPath], None] = []
    name: str
    description: Union[str, None ]
    targetWindow: TargetWindow
    status: Status
    adUnitCode: str
    adUnitSizes: list[AdUnitSize]
    isInterstitial: bool
    isNative: bool
    isFluid: bool
    explicitlyTargeted: bool
    adSenseSettings: AdSensingSettings
    adSenseSettingsSource: AdsensingSettingsSource
    appliedLabelFrequencyCaps: list[LabelFrequencyCap]
    effectiveLabelFrequencyCaps: list[LabelFrequencyCap]
    appliedLabels: list[AppliedLabel]
    effectiveAppliedLabels: list[AppliedLabel]
    effectiveTeamIds: list[str]
    appliedTeamIds: list[str]
    # lastModifiedDateTime: datetime
    smartSizeMode: SmartSizeMode
    isSetTopBoxEnabled: bool
    refreshRate: Optional[Union[str, None]] = Field(default=None)
    externalSetTopBoxChannelId: Optional[Union[str, None]] = Field(default=None)
    isSetTopBoxEnabled: bool
    applicationId: Optional[Union[str, None]] = Field(default=None)

    model_config = ConfigDict(
        use_enum_values=True,
        coerce_numbers_to_str=True
    )

    # @field_validator("lastModifiedDateTime", mode='before')
    # def zeep_2_dt_obj(cls, value, values):
    #     return DateTime(**value).date_time_object