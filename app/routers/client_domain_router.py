from fastapi import APIRouter, Depends
from app.schemas.client_domain_schema import (
    DomainConfigUpdate,
    DomainConfigResponse
)
from app.services.client_domain_service import (
    get_domain_config,
    upsert_domain_config
)
from app.utils.dependencies import get_current_client


router = APIRouter(
    prefix="/client/domain",
    tags=["Client Domain"]
)


@router.get("/", response_model=DomainConfigResponse)
def fetch_domain_config(
    token_data = Depends(get_current_client)
):
    token_data, db = token_data
    client_id = token_data.id

    record = get_domain_config(client_id, db)

    if not record:
        return None

    return record


@router.post("/", response_model=DomainConfigResponse)
def save_domain_config(
    payload: DomainConfigUpdate,
    token_data = Depends(get_current_client),
):
    token_data, db = token_data
    client_id = token_data.id

    record = upsert_domain_config(client_id, payload, db)
    return record