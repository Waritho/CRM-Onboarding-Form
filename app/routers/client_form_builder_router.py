from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.utils.dependencies import get_current_client

from app.schemas.client_form_builder_schema import (
    FormConfigCreate,
    FormConfigResponse
)

from app.services.client_form_builder_service import (
    upsert_form_config,
    get_form_config
)

router = APIRouter(
    prefix="/client/form-builder",
    tags=["Client Form Builder"]
)


# UPSERT FORM CONFIG

@router.post("/config")
def create_or_update_form_config(
    payload: FormConfigCreate,
    current_client = Depends(get_current_client)
):
    current_client, db = current_client

    upsert_form_config(
        db=db,
        client_id=current_client.id,
        payload=payload
    )

    return {"message": "Form configuration saved successfully"}


# GET FORM CONFIG

@router.get("/config", response_model=FormConfigResponse)
def fetch_form_config(
    current_client = Depends(get_current_client)
):
    current_client, db = current_client

    data = get_form_config(
        db=db,
        client_id=current_client.id
    )

    return data