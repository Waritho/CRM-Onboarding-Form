from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.client_domain_config import ClientDomainConfig


def get_domain_config(client_id: int, db: Session):

    record = db.query(ClientDomainConfig).filter(
        ClientDomainConfig.client_id == client_id
    ).first()

    return record


def upsert_domain_config(client_id: int, data, db: Session):

    record = db.query(ClientDomainConfig).filter(
        ClientDomainConfig.client_id == client_id
    ).first()

    if not record:
        record = ClientDomainConfig(client_id=client_id)
        db.add(record)

    record.main_domain = data.main_domain.strip().lower()
    record.subdomain = data.subdomain.strip().lower()

    try:
        db.commit()
        db.refresh(record)
        return record

    except IntegrityError as e:
        db.rollback()

        # Likely duplicate main_domain or subdomain
        raise HTTPException(
            status_code=400,
            detail="Domain or subdomain already in use"
        )