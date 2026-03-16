from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, UploadFile

from app.models.crm_migration_documents import CRMMigrationDocument
from app.models.document_types import DocumentType
from app.models.client_crm_info import ClientCRMInfo
from app.utils.s3_handler import upload_to_s3, generate_presigned_url, delete_from_s3


# GET ALL DOCUMENTS FOR CLIENT
def get_client_documents(client_id: int, db: Session):

    # check crm usage
    crm_info = db.query(ClientCRMInfo).filter(
        ClientCRMInfo.client_id == client_id
    ).first()

    if not crm_info or crm_info.using_crm is False:
        return []

    doc_types = db.query(DocumentType).filter(
        DocumentType.is_active == True
    ).all()

    client_docs = db.query(CRMMigrationDocument).filter(
        CRMMigrationDocument.client_id == client_id
    ).all()

    doc_map = {d.document_type_id: d for d in client_docs}

    response = []

    for dt in doc_types:
        doc = doc_map.get(dt.id)

        response.append({
            "document_type_id": dt.id,
            "name": dt.name,
            "file_path": generate_presigned_url(doc.file_path) if doc and doc.file_path else None
        })

    return response


# UPLOAD OR REPLACE DOCUMENT
def upload_document(
    client_id: int,
    document_type_id: int,
    file: UploadFile,
    db: Session
):

    # -------- CHECK CRM ENABLED --------
    crm_info = db.query(ClientCRMInfo).filter(
        ClientCRMInfo.client_id == client_id
    ).first()

    if not crm_info or crm_info.using_crm is False:
        raise HTTPException(
            status_code=400,
            detail="CRM not enabled for this client"
        )

    # -------- VALIDATE DOCUMENT TYPE --------
    doc_type = db.query(DocumentType).filter(
        DocumentType.id == document_type_id,
        DocumentType.is_active == True
    ).first()

    if not doc_type:
        raise HTTPException(status_code=404, detail="Invalid document type")

    # -------- UPLOAD TO S3 --------
    file_path = upload_to_s3(
        file=file,
        folder=f"migration/client_{client_id}/document_type_{document_type_id}"
    )

    # -------- UPSERT DB --------
    record = db.query(CRMMigrationDocument).filter(
        CRMMigrationDocument.client_id == client_id,
        CRMMigrationDocument.document_type_id == document_type_id
    ).first()

    try:
        if not record:
            new_doc = CRMMigrationDocument(
                client_id=client_id,
                document_type_id=document_type_id,
                file_path=file_path
            )
            db.add(new_doc)

        else:
            # replace old file path
            record.file_path = file_path

        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")

    return {"message": "File uploaded successfully"}


# DELETE DOCUMENT
def delete_document(
    client_id: int,
    document_type_id: int,
    db: Session
):
    record = db.query(CRMMigrationDocument).filter(
        CRMMigrationDocument.client_id == client_id,
        CRMMigrationDocument.document_type_id == document_type_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from S3
    if record.file_path:
        delete_from_s3(record.file_path)

    try:
        db.delete(record)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")

    return {"message": "Document deleted successfully"}