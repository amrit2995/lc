from pydantic import BaseModel, field_validator, ConfigDict, Field, computed_field
from datetime import datetime
from typing import Optional, Union
import pytz


class Date(BaseModel):
    year: int
    month: int
    day: int

class DateTime(BaseModel):
    date: Date
    hour: int
    minute: int
    second: int
    timeZoneId: str

    @property
    def date_time_object(self) -> datetime:
        dt_obj = datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
        )

        import pytz
        gam_tz = pytz.timezone(self.timeZoneId)
        dt_obj = gam_tz.localize(dt_obj)
        return dt_obj.astimezone(pytz.utc)

class Stats(BaseModel):
    impressionsDelivered: int
    clicksDelivered: int

class OrderLevelModel(BaseModel):
    id: int
    name: Optional[str]
    unlimitedEndDateTime: Optional[bool]
    startDateTime: Optional[datetime]
    endDateTime: Union[Optional[datetime]]
    totalClicksDelivered: Optional[int]
    totalImpressionsDelivered: Optional[int]

    @field_validator("startDateTime", "endDateTime", mode='before')
    def zeep_2_dt_obj(cls, value, values):
        if value:
            return DateTime(**value).date_time_object

class LineItemModel(BaseModel):
    id: int
    name: Optional[str]
    unlimitedEndDateTime: Optional[bool]
    orderId: int
    startDateTime: Optional[datetime]
    endDateTime: Optional[datetime]
    stats: Union[Stats, None] = Field(exclude=True)

    @computed_field(return_type=int)
    @property
    def totalClicksDelivered(self) -> int:
        return self.stats.clicksDelivered if self.stats else None

    @computed_field(return_type=int)
    @property
    def totalImpressionsDelivered(self) -> int:
        return self.stats.impressionsDelivered if self.stats else None

    @field_validator("startDateTime", "endDateTime", mode='before')
    def zeep_2_dt_obj(cls, value, values):
        if value:
            return DateTime(**value).date_time_object