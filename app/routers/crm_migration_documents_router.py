from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.crm_migration_documents_service import (
    get_client_documents,
    upload_document
)
from app.schemas.crm_migration_documents_schema import DocumentListResponse
from app.utils.dependencies import get_current_client


router = APIRouter(
    prefix="/client/crm-documents",
    tags=["CRM Migration Documents"]
)


# GET ALL DOCUMENTS
@router.get("/", response_model=DocumentListResponse)
def fetch_documents(
    token_data = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    client_id = token_data.id

    docs = get_client_documents(client_id, db)
    return {"documents": docs}


# UPLOAD DOCUMENT
@router.post("/upload/{document_type_id}")
def upload_client_document(
    document_type_id: int,
    file: UploadFile = File(...),
    token_data = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    client_id = token_data.id

    result = upload_document(client_id, document_type_id, file, db)
    return result