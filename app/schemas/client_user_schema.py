from pydantic import BaseModel, EmailStr
from datetime import datetime

class ClientUserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    can_write: bool = True

class ClientUserCreate(BaseModel):
    email: EmailStr
    can_write: bool = True

class ClientUserUpdate(BaseModel):
    can_write: bool

class ClientUserResponse(ClientUserBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
