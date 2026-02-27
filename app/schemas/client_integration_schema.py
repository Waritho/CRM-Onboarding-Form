from pydantic import BaseModel
from typing import List, Dict, Any


class IntegrationConfig(BaseModel):
    integration_id: int
    is_enabled: bool
    config: Dict[str, Any] = {}


class IntegrationConfigResponse(BaseModel):
    integration_id: int
    name: str
    is_enabled: bool
    config: Dict[str, Any]


class IntegrationListResponse(BaseModel):
    integrations: List[IntegrationConfigResponse]