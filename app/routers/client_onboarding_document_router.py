from fastapi import APIRouter, Depends, File, UploadFile, Form
from app.utils.dependencies import get_current_client
from app.utils.submission_guard import ensure_not_submitted
from app.utils.s3_handler import upload_to_s3, generate_presigned_url

from app.schemas.client_onboarding_document_schema import (
    DocumentResponse
)

from app.services.client_onboarding_document_service import (
    get_all_documents,
    upload_or_replace_document,
    validate_mandatory_documents
)


router = APIRouter(
    prefix="/client/onboarding-documents",
    tags=["Client Onboarding Documents"]
)


@router.get("/", response_model=list[DocumentResponse])
def fetch_documents(
    token_data = Depends(get_current_client)
):
    token_data, db = token_data
    client_id = token_data.id

    documents = get_all_documents(client_id, db)
    
    # Generate presigned URLs for each document URL
    for doc in documents:
        if hasattr(doc, "url") and doc.url:
            doc.url = generate_presigned_url(doc.url)
            
    return documents


@router.post("/")
def upload_document(
    code: str = Form(...),
    file: UploadFile = File(...),
    token_data = Depends(get_current_client)
):
    token_data, db = token_data
    ensure_not_submitted((token_data, db))
    client_id = token_data.id

    # Use the S3 utility to upload
    s3_object_key = upload_to_s3(
        file=file,
        folder=f"onboarding/client_{client_id}"
    )

    return upload_or_replace_document(
        client_id,
        code,
        s3_object_key,
        db
    )


@router.get("/validate")
def validate_documents(
    token_data = Depends(get_current_client)
):
    token_data, db = token_data
    client_id = token_data.id

    return {
        "all_mandatory_uploaded": validate_mandatory_documents(client_id, db)
    }