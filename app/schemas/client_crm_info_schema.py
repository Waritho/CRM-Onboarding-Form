from pydantic import BaseModel
from typing import Optional


class CRMInfoUpdate(BaseModel):
    using_crm: bool
    crm_name: Optional[str] = None
    want_data_migration: Optional[bool] = False
    previous_crm_name: Optional[str] = None


class CRMInfoResponse(BaseModel):
    using_crm: bool
    crm_name: Optional[str]
    want_data_migration: bool
    previous_crm_name: Optional[str]

    class Config:
        from_attributes = True