from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.client_integration_schema import (
    IntegrationConfig,
    IntegrationListResponse
)
from app.services.client_integrations_service import (
    get_client_integrations,
    upsert_client_integrations
)

# your jwt dependency (same used everywhere)
from app.utils.dependencies import get_current_client 


router = APIRouter(
    prefix="/client/integrations",
    tags=["Client Integrations"]
)


# GET FULL INTEGRATIONS FORM
@router.get("/", response_model=IntegrationListResponse)
def fetch_integrations(
    token_data: dict = Depends(get_current_client),
    
):
    token_data , db = token_data
    client_id = token_data.id

    integrations = get_client_integrations(client_id, db)

    return {"integrations": integrations}


# UPSERT FULL FORM
@router.post("/")
def save_integrations(
    payload: List[IntegrationConfig],
    token_data: dict = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    client_id = token_data.id

    result = upsert_client_integrations(client_id, payload, db)
    return result