from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_client
from app.schemas.client_schema import (
    ClientBasicDetailsSchema,
    ClientBasicDetailsResponse
)
from app.services.client_service import (
    upsert_basic_details,
    get_basic_details
)

router = APIRouter(prefix="/client", tags=["Client"])


# CREATE OR UPDATE (UPSERT)
@router.post("/basic-details", response_model=ClientBasicDetailsResponse)
def save_basic_details(
    data: ClientBasicDetailsSchema,
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    return upsert_basic_details(current_client.id, data, db)


# GET BASIC DETAILS
@router.get("/basic-details", response_model=ClientBasicDetailsResponse)
def fetch_basic_details(
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    details = get_basic_details(current_client.id, db)

    if not details:
        raise HTTPException(status_code=404, detail="Details not found")
    return details


# PUT UPDATE (OPTIONAL EXPLICIT)
@router.put("/basic-details", response_model=ClientBasicDetailsResponse)
def update_basic_details(
    data: ClientBasicDetailsSchema,
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    return upsert_basic_details(current_client.id, data, db)