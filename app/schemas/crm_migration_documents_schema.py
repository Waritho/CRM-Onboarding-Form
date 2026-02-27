from pydantic import BaseModel
from typing import List, Optional


class DocumentItem(BaseModel):
    document_type_id: int
    name: str
    file_path: Optional[str]


class DocumentListResponse(BaseModel):
    documents: List[DocumentItem]