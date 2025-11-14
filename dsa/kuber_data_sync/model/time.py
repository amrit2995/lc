from pydantic import BaseModel
from datetime import datetime,timezone
from kuber_data_sync.configs import CommonConfigs

#### Common Date Time Models #####

__all__ = [
    "Date",
    "Datetime"
]

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
        return dt_obj.astimezone(pytz.timezone(CommonConfigs.TIMEZONE))
    
    def get_current_datetime_with_millis() -> datetime:
        import pytz
        utc = pytz.utc
        target_tz = pytz.timezone(CommonConfigs.TIMEZONE)
        utc_now = utc.localize(datetime.now())  # aware datetime in UTC
        return utc_now.astimezone(target_tz)