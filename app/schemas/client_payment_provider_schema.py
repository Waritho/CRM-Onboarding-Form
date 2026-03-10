from pydantic import BaseModel
from typing import Dict, Any, List


class PaymentProviderRequest(BaseModel):
    provider: str
    credentials: Dict[str, Any]


class PaymentProviderResponse(BaseModel):
    provider: str
    is_enabled: bool
    credentials: Dict[str, Any]

    class Config:
        from_attributes = True


class PaymentProviderHydrationResponse(BaseModel):
    provider_code: str
    provider_name: str
    is_enabled: bool
    required_fields: List[str]
    credentials: Dict[str, Any]

    class Config:
        from_attributes = True