from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    code: str
    file_url: str


class DocumentResponse(BaseModel):
    code: str
    name: str
    is_mandatory: bool
    file_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True