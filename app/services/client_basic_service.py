from sqlalchemy.orm import Session
from app.models.client_basic_details import ClientBasicDetails


def upsert_basic_details(client_id: int, data, db: Session):

    existing = (
        db.query(ClientBasicDetails)
        .filter(ClientBasicDetails.client_id == client_id)
        .first()
    )

    if existing:
        # update
        existing.institution_name = data.institution_name
        existing.country = data.country
        existing.state = data.state
        existing.city = data.city
        existing.address = data.address
        existing.website = data.website

        db.commit()
        db.refresh(existing)

        return existing

    # create
    new_entry = ClientBasicDetails(
        client_id=client_id,
        institution_name=data.institution_name,
        country=data.country,
        state=data.state,
        city=data.city,
        address=data.address,
        website=data.website
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


def get_basic_details(client_id: int, db: Session):

    return (
        db.query(ClientBasicDetails)
        .filter(ClientBasicDetails.client_id == client_id)
        .first()
    )