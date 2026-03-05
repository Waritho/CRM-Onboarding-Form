from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.client_crm_info_schema import (
    CRMInfoUpdate,
    CRMInfoResponse
)
from app.services.client_crm_info_service import (
    get_crm_info,
    upsert_crm_info
)

from app.utils.dependencies import get_current_client
from app.utils.submission_guard import ensure_not_submitted


router = APIRouter(
    prefix="/client/crm-info",
    tags=["Client CRM Info"]
)


# GET CRM INFO
@router.get("/", response_model=CRMInfoResponse)
def fetch_crm_info(
    token_data = Depends(get_current_client)
):
    token_data, db = token_data
    client_id = token_data.id

    record = get_crm_info(client_id, db)
    return record


# UPSERT CRM INFO
@router.post("/", response_model=CRMInfoResponse)
def save_crm_info(
    payload: CRMInfoUpdate,
    token_data = Depends(get_current_client),
    
):
    token_data, db = token_data
    ensure_not_submitted((token_data, db))
    client_id = token_data.id

    record = upsert_crm_info(client_id, payload, db)
    return record