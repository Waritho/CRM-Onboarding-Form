from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.client_crm_info import ClientCRMInfo


# GET CRM INFO
def get_crm_info(client_id: int, db: Session):

    record = db.query(ClientCRMInfo).filter(
        ClientCRMInfo.client_id == client_id
    ).first()

    if not record:
        # lazy create default row
        new_record = ClientCRMInfo(client_id=client_id)

        try:
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            return new_record
        except IntegrityError:
            db.rollback()
            return db.query(ClientCRMInfo).filter(
                ClientCRMInfo.client_id == client_id
            ).first()

    return record


# UPSERT CRM INFO
def upsert_crm_info(client_id: int, data, db: Session):

    record = db.query(ClientCRMInfo).filter(
        ClientCRMInfo.client_id == client_id
    ).first()

    if not record:
        record = ClientCRMInfo(client_id=client_id)
        db.add(record)

    # ---------------- LOGIC ---------------- #

    if data.using_crm is False:
        record.using_crm = False
        record.crm_name = None
        record.want_data_migration = False
        record.previous_crm_name = None

    else:
        # using crm true
        if not data.crm_name:
            raise HTTPException(status_code=400, detail="CRM name required")

        record.using_crm = True
        record.crm_name = data.crm_name

        record.want_data_migration = data.want_data_migration

        if data.want_data_migration:
            if not data.previous_crm_name:
                raise HTTPException(status_code=400, detail="Previous CRM name required")

            record.previous_crm_name = data.previous_crm_name
        else:
            record.previous_crm_name = None

    try:
        db.commit()
        db.refresh(record)
        return record

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")