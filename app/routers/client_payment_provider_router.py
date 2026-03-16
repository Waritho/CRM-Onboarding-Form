from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_client, require_write_access

from app.schemas.client_payment_provider_schema import (
    PaymentProviderRequest,
    PaymentProviderResponse,
    PaymentProviderHydrationResponse
)

from app.services.client_payment_provider_service import (
    get_payment_providers,
    upsert_payment_provider,
    disable_payment_provider
)


router = APIRouter(
    prefix="/client/payment",
    tags=["Client Payment Providers"]
)


@router.get("/", response_model=list[PaymentProviderHydrationResponse])
def fetch_providers(
    token_data = Depends(get_current_client)
):
    token_data, db = token_data
    client_id = token_data.id

    return get_payment_providers(client_id, db)


@router.post("/")
def save_provider(
    payload: PaymentProviderRequest,
    token_data = Depends(require_write_access)
):
    token_data, db = token_data
    client_id = token_data.id

    return upsert_payment_provider(
        client_id,
        payload.provider,
        payload.credentials,
        db
    )


@router.post("/disable/{provider}")
def disable_provider(
    provider: str,
    token_data = Depends(require_write_access)
):
    token_data, db = token_data
    client_id = token_data.id

    return disable_payment_provider(client_id, provider, db)