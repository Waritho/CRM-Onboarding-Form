from fastapi import APIRouter, Depends, File, UploadFile, Form
from app.utils.dependencies import get_current_client
from app.utils.cloudinary_handler import upload_to_cloudinary

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

    return get_all_documents(client_id, db)


@router.post("/")
def upload_document(
    code: str = Form(...),
    file: UploadFile = File(...),
    token_data = Depends(get_current_client)
):
    token_data, db = token_data
    client_id = token_data.id

    # Use the utility to upload
    cloudinary_url = upload_to_cloudinary(
        file=file,
        folder=f"onboarding/client_{client_id}"
    )

    return upload_or_replace_document(
        client_id,
        code,
        cloudinary_url,
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