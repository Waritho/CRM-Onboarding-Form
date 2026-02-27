from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.POC_details import ClientPOC


# CREATE NEW POC
def create_new_poc(client_id: int, data, db: Session):

    # Check duplicate email per client
    existing_email = db.query(ClientPOC).filter(
        ClientPOC.client_id == client_id,
        ClientPOC.email == data.email
    ).first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Check duplicate mobile per client
    existing_mobile = db.query(ClientPOC).filter(
        ClientPOC.client_id == client_id,
        ClientPOC.mobile == data.mobile
    ).first()

    if existing_mobile:
        raise HTTPException(status_code=400, detail="Mobile already exists")

    # If first POC for client → make primary automatically
    first_poc = db.query(ClientPOC).filter(
        ClientPOC.client_id == client_id
    ).first()

    is_primary = False  
    if not first_poc:
        is_primary = True

    new_poc = ClientPOC(
        client_id=client_id,
        name=data.name,
        email=data.email,
        mobile=data.mobile,
        is_primary=is_primary
    )

    try:
        db.add(new_poc)
        db.commit()
        db.refresh(new_poc)
        return new_poc

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")


# GET ALL POCS
def get_pocs_by_client(client_id: int, db: Session):
    return db.query(ClientPOC).filter(
        ClientPOC.client_id == client_id
    ).order_by(ClientPOC.id.desc()).all()


# UPDATE POC
def update_poc(client_id: int, poc_id: int, data, db: Session):

    poc = db.query(ClientPOC).filter(
        ClientPOC.client_id == client_id,
        ClientPOC.id == poc_id
    ).first()

    if not poc:
        raise HTTPException(status_code=404, detail="POC not found")

    # NAME UPDATE
    if data.name is not None:
        poc.name = data.name

    # EMAIL UPDATE
    if data.email is not None:

        existing_email = db.query(ClientPOC).filter(
            ClientPOC.client_id == client_id,
            ClientPOC.email == data.email,
            ClientPOC.id != poc_id
        ).first()

        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        poc.email = data.email

    # MOBILE UPDATE
    if data.mobile is not None:

        existing_mobile = db.query(ClientPOC).filter(
            ClientPOC.client_id == client_id,
            ClientPOC.mobile == data.mobile,
            ClientPOC.id != poc_id
        ).first()

        if existing_mobile:
            raise HTTPException(status_code=400, detail="Mobile already exists")

        poc.mobile = data.mobile

    try:
        db.commit()
        db.refresh(poc)
        return poc

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")
