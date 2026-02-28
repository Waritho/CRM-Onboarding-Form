from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.onboarding_document_master import OnboardingDocumentMaster
from app.models.client_onboarding_documents import ClientOnboardingDocument

# GET ALL DOCUMENTS

def get_all_documents(client_id: int, db: Session):

    masters = db.query(OnboardingDocumentMaster).all()

    client_docs = db.query(ClientOnboardingDocument).filter(
        ClientOnboardingDocument.client_id == client_id
    ).all()

    client_map = {doc.document_id: doc for doc in client_docs}

    response = []

    for master in masters:
        uploaded = client_map.get(master.id)

        response.append({
            "code": master.code,
            "name": master.name,
            "is_mandatory": master.is_mandatory,
            "file_url": uploaded.file_url if uploaded else None,
            "uploaded_at": uploaded.uploaded_at if uploaded else None
        })

    return response

# Upload / Replace Logic

def upload_or_replace_document(client_id: int, code: str, file_url: str, db: Session):

    master = db.query(OnboardingDocumentMaster).filter(
        OnboardingDocumentMaster.code == code
    ).first()

    if not master:
        raise HTTPException(status_code=404, detail="Invalid document code")

    record = db.query(ClientOnboardingDocument).filter(
        ClientOnboardingDocument.client_id == client_id,
        ClientOnboardingDocument.document_id == master.id
    ).first()

    if not record:
        record = ClientOnboardingDocument(
            client_id=client_id,
            document_id=master.id,
            file_url=file_url
        )
        db.add(record)
    else:
        record.file_url = file_url

    try:
        db.commit()
        db.refresh(record)
        return record

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")
    
# Validate Mandatory Completion
def validate_mandatory_documents(client_id: int, db: Session):

    masters = db.query(OnboardingDocumentMaster).filter(
        OnboardingDocumentMaster.is_mandatory == True
    ).all()

    mandatory_ids = [m.id for m in masters]

    uploaded = db.query(ClientOnboardingDocument).filter(
        ClientOnboardingDocument.client_id == client_id,
        ClientOnboardingDocument.document_id.in_(mandatory_ids)
    ).all()

    if len(uploaded) != len(mandatory_ids):
        return False

    return True