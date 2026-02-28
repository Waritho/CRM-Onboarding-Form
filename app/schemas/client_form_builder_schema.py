from pydantic import BaseModel
from typing import List, Optional


# FIELD CONFIG

class FieldConfigCreate(BaseModel):
    field_id: int
    is_enabled: bool
    is_required: bool


class FieldConfigResponse(FieldConfigCreate):
    id: int

    class Config:
        from_attributes = True


# SECTION CONFIG

class SectionConfigCreate(BaseModel):
    section_id: int
    is_enabled: bool
    comment_text: Optional[str] = None
    fields: List[FieldConfigCreate]


class SectionConfigResponse(BaseModel):
    id: int
    section_id: int
    is_enabled: bool
    comment_text: Optional[str]
    fields: List[FieldConfigResponse]

    class Config:
        from_attributes = True


# FULL FORM CONFIG (UPSERT)

class FormConfigCreate(BaseModel):
    sections: List[SectionConfigCreate]


class FormConfigResponse(BaseModel):
    sections: List[SectionConfigResponse]