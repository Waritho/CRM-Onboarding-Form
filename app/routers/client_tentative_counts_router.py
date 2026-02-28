from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.client_tentative_counts_schema import (
    TentativeCountsResponse,TentativeCountsUpsert
)
from app.services.client_tentative_counts_service import (
    upsert_tentative_counts,
    get_tentative_counts
)

from app.utils.dependencies import get_current_client

router = APIRouter(prefix="/client/tentative-counts",tags=["Client Tentative Counts"])


# GET TENTATIVE COUNTS
@router.get("/", response_model=TentativeCountsResponse)
def fetch_tentative_counts(
    current_user=Depends(get_current_client)
):
    current_user , db = current_user
    client_id = current_user.id

    record = get_tentative_counts(client_id, db)
    return record


# UPSERT TENTATIVE COUNTS
@router.post("/", response_model=TentativeCountsResponse)
def save_tentative_counts(
    data: TentativeCountsUpsert,
    current_user=Depends(get_current_client)
):
    current_user , db = current_user
    client_id = current_user.id

    record = upsert_tentative_counts(client_id, data, db)
    return record