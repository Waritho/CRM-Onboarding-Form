from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.client_tentative_counts import ClientTentativeCounts


# UPSERT TENTATIVE COUNTS (CREATE OR REPLACE)
def upsert_tentative_counts(client_id: int, data, db: Session):

    record = db.query(ClientTentativeCounts).filter(
        ClientTentativeCounts.client_id == client_id
    ).first()

    # CREATE
    if not record:
        new_record = ClientTentativeCounts(
            client_id=client_id,
            lead_intake=data.lead_intake or 0,
            application_count=data.application_count or 0,
            raw_data_count=data.raw_data_count or 0,
            crm_count=data.crm_count or 0,
            widget_count=data.widget_count or 0
        )

        try:
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            return new_record

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error")

    # UPDATE (FULL REPLACE)
    record.lead_intake = data.lead_intake 
    record.application_count = data.application_count 
    record.raw_data_count = data.raw_data_count 
    record.crm_count = data.crm_count
    record.widget_count = data.widget_count

    try:
        db.commit()
        db.refresh(record)
        return record

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")


# GET TENTATIVE COUNTS FOR CLIENT
def get_tentative_counts(client_id: int, db: Session):

    record = db.query(ClientTentativeCounts).filter(
        ClientTentativeCounts.client_id == client_id
    ).first()

    if not record:
        # Create and save empty default structure if not filled yet
        new_record = ClientTentativeCounts(
            client_id=client_id,
            lead_intake=0,
            application_count=0,
            raw_data_count=0,
            crm_count=0,
            widget_count=0
        )
        try:
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            return new_record
        except IntegrityError:
            db.rollback()
            # If record was created by concurrent request, fetch it
            return db.query(ClientTentativeCounts).filter(
                ClientTentativeCounts.client_id == client_id
            ).first()

    return record