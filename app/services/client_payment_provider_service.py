from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.client_payment_provider import ClientPaymentProvider
from app.utils.payment_provider_validators import (
    validate_razorpay,
    validate_easy_buzz,
    validate_ezypay,
    validate_hdfc,
    validate_payu
)


VALIDATOR_MAP = {
    "razorpay": validate_razorpay,
    "easy_buzz": validate_easy_buzz,
    "ezypay": validate_ezypay,
    "hdfc": validate_hdfc,
    "payu": validate_payu,
}


def get_payment_providers(client_id: int, db: Session):
    return db.query(ClientPaymentProvider).filter(
        ClientPaymentProvider.client_id == client_id
    ).all()


def upsert_payment_provider(client_id: int, provider: str, credentials: dict, db: Session):

    if provider not in VALIDATOR_MAP:
        raise HTTPException(status_code=400, detail="Invalid provider")

    validator = VALIDATOR_MAP[provider]

    if not validator(credentials):
        raise HTTPException(status_code=400, detail="Invalid credentials payload")

    record = db.query(ClientPaymentProvider).filter(
        ClientPaymentProvider.client_id == client_id,
        ClientPaymentProvider.provider == provider
    ).first()

    if not record:
        record = ClientPaymentProvider(
            client_id=client_id,
            provider=provider,
            credentials=credentials,
            is_enabled=True
        )
        db.add(record)
    else:
        record.credentials = credentials
        record.is_enabled = True

    try:
        db.commit()
        db.refresh(record)
        return record

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")


def disable_payment_provider(client_id: int, provider: str, db: Session):

    record = db.query(ClientPaymentProvider).filter(
        ClientPaymentProvider.client_id == client_id,
        ClientPaymentProvider.provider == provider
    ).first()

    if not record:
        return None

    record.is_enabled = False
    db.commit()
    return record