from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_client

from app.schemas.poc_schema import (
    ClientPOCCreate,
    ClientPOCUpdate,
    ClientPOCResponse
)

from app.services.poc_service import (
    create_new_poc,
    get_pocs_by_client,
    update_poc
)

router = APIRouter(
    prefix="/client/pocs", tags=["Client POC"])


# CREATE POC
@router.post("", response_model=ClientPOCResponse)
def create_poc(
    data: ClientPOCCreate,
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    return create_new_poc(current_client.id, data, db)


# GET ALL POCS
@router.get("", response_model=list[ClientPOCResponse])
def get_all_pocs(
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    return get_pocs_by_client(current_client.id, db)


# UPDATE POC
@router.put("/{poc_id}", response_model=ClientPOCResponse)
def update_poc_details(
    poc_id: int,
    data: ClientPOCUpdate,
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    return update_poc(current_client.id, poc_id, data, db)