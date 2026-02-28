from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


# Set your local timezone here
LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")


class TentativeCountsBase(BaseModel):
    lead_intake: Optional[int] = Field(default=0, ge=0)
    application_count: Optional[int] = Field(default=0, ge=0)
    raw_data_count: Optional[int] = Field(default=0, ge=0)
    crm_count: Optional[int] = Field(default=0, ge=0)
    widget_count: Optional[int] = Field(default=0, ge=0)


class TentativeCountsUpsert(TentativeCountsBase):
    pass


class TentativeCountsResponse(BaseModel):
    id: int
    client_id: int

    lead_intake: int
    application_count: int
    raw_data_count: int
    crm_count: int
    widget_count: int

    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def convert_utc_to_local(self, value: datetime) -> datetime:
        """
        Ensures:
        - If datetime is naive, assume it's UTC
        - Convert to configured local timezone
        """
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(LOCAL_TIMEZONE)

    class Config:
        from_attributes = True