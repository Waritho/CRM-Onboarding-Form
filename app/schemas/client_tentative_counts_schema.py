from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


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

    class Config:
        from_attributes = True