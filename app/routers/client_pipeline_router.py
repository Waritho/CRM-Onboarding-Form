from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_client

from app.schemas.client_pipeline_schema import (
    PipelineConfigCreate,
    PipelineConfigResponse
)

from app.services.client_pipeline_service import (
    upsert_pipeline_config,
    get_pipeline_config
)

router = APIRouter(
    prefix="/client/pipeline",
    tags=["Client Lead Pipeline"]
)


# UPSERT PIPELINE
@router.post("/config")
def create_or_update_pipeline(
    payload: PipelineConfigCreate,
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    upsert_pipeline_config(
        db=db,
        client_id=current_client.id,
        payload=payload
    )

    return {"message": "Pipeline configuration saved"}


# GET PIPELINE
@router.get("/config", response_model=PipelineConfigResponse)
def fetch_pipeline(
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    data = get_pipeline_config(db, current_client.id)
    return data