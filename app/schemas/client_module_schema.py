from pydantic import BaseModel
from typing import List, Optional


# SINGLE MODULE RESPONSE
class ModuleItemResponse(BaseModel):
    module_id: int
    module_name: str
    is_enabled: bool

    class Config:
        from_attributes = True


# GET FULL RESPONSE
class ClientModulesResponse(BaseModel):
    modules: List[ModuleItemResponse]
    comment: Optional[str] = None


# CREATE / UPDATE REQUEST
class ClientModulesUpsertRequest(BaseModel):
    selected_module_ids: List[int]
    comment: Optional[str] = None