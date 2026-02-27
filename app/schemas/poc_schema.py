from pydantic import BaseModel, EmailStr
from typing import Optional


# CREATE
class ClientPOCCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    is_primary: bool = False


# UPDATE
class ClientPOCUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    is_primary: Optional[bool] = None


# RESPONSE
class ClientPOCResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    is_primary: bool

    class Config:
        from_attributes = True #It tells Pydantic:

'''
"Hey, this is not a dict.
This is a SQLAlchemy object.
Read values from object attributes.
So it converts
Into JSON automatically.'''