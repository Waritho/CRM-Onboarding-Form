from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.client_payment_provider import ClientPaymentProvider
from app.models.payment_provider_master import PaymentProviderMaster


def get_payment_providers(client_id: int, db: Session):
    # 1. Fetch all active master providers
    masters = db.query(PaymentProviderMaster).filter(
        PaymentProviderMaster.is_active == True
    ).all()

    # 2. Fetch all client-configured providers
    client_configs = db.query(ClientPaymentProvider).filter(
        ClientPaymentProvider.client_id == client_id
    ).all()

    # 3. Create a map for O(1) lookup
    client_map = {cfg.provider: cfg for cfg in client_configs}

    # 4. Merge master data with client state
    response = []
    for master in masters:
        client_cfg = client_map.get(master.code)
        response.append({
            "provider_code": master.code,
            "provider_name": master.display_name,
            "is_enabled": client_cfg.is_enabled if client_cfg else False,
            "required_fields": master.required_fields,
            "credentials": client_cfg.credentials if client_cfg else {}
        })

    return response


def upsert_payment_provider(client_id: int, provider_code: str, credentials: dict, db: Session):
    # 1. Fetch master provider record
    master = db.query(PaymentProviderMaster).filter(
        PaymentProviderMaster.code == provider_code,
        PaymentProviderMaster.is_active == True
    ).first()

    if not master:
        raise HTTPException(status_code=400, detail="Invalid or inactive payment provider")

    # 2. Dynamic Validation: Check if all required fields are present
    required_fields = master.required_fields or []
    missing_fields = [f for f in required_fields if f not in credentials]
    
    if missing_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required credential fields: {', '.join(missing_fields)}"
        )

    # 3. Fetch or Create client-specific record
    record = db.query(ClientPaymentProvider).filter(
        ClientPaymentProvider.client_id == client_id,
        ClientPaymentProvider.provider == provider_code
    ).first()

    if not record:
        record = ClientPaymentProvider(
            client_id=client_id,
            provider=provider_code,
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
        raise HTTPException(status_code=400, detail="Database error or duplicate record")


def disable_payment_provider(client_id: int, provider_code: str, db: Session):
    record = db.query(ClientPaymentProvider).filter(
        ClientPaymentProvider.client_id == client_id,
        ClientPaymentProvider.provider == provider_code
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Payment provider configuration not found")

    record.is_enabled = False
    db.commit()
    return record
