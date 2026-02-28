from pydantic import BaseModel
from typing import Dict, Any


class PaymentProviderRequest(BaseModel):
    provider: str
    credentials: Dict[str, Any]


class PaymentProviderResponse(BaseModel):
    provider: str
    is_enabled: bool
    credentials: Dict[str, Any]

    class Config:
        from_attributes = True