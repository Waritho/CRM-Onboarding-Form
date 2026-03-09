from pydantic import BaseModel
from typing import List, Optional


# FIELD CONFIG

class FieldConfigCreate(BaseModel):
    field_id: int
    is_enabled: bool


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


# ──────────────────────────────────────────────────────────────────────────────
# UI HYDRATION SCHEMAS  (GET /config  →  Frontend)
# These schemas carry EVERYTHING the frontend needs to render the form
# builder UI dynamically: master metadata (name, label, field_type) merged
# with the per-client state (is_enabled).
# ──────────────────────────────────────────────────────────────────────────────

class FieldUIResponse(BaseModel):
    """A single field row as the frontend receives it."""
    # Master identity — used as the hidden key when submitting back
    field_id: int
    field_key: str          # e.g. "first_name"  — stable string alias
    label: str              # e.g. "First Name"  — display text
    field_type: str         # e.g. "text" | "select" | "date" | "boolean" | "document"
    sort_order: int

    # Per-client state — what the user actually configured
    is_enabled: bool

    class Config:
        from_attributes = True


class SectionUIResponse(BaseModel):
    """A single form section as the frontend receives it."""
    # Master identity
    section_id: int
    code: str               # e.g. "personal_details"
    name: str               # e.g. "Personal Details"
    is_repeatable: bool
    sort_order: int

    # Per-client state
    is_enabled: bool
    comment_text: Optional[str]

    fields: List[FieldUIResponse]

    class Config:
        from_attributes = True


class FormUIConfigResponse(BaseModel):
    """Top-level response for GET /config."""
    client_id: int
    sections: List[SectionUIResponse]