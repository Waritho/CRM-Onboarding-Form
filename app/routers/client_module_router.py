from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_client

from app.schemas.client_module_schema import (
    ClientModulesResponse,
    ClientModulesUpsertRequest
)

from app.services.client_module_service import (
    get_client_modules,
    upsert_client_modules
)

router = APIRouter(prefix="/client/modules", tags=["Client Modules"])


# GET MODULE CONFIGURATION
@router.get("", response_model=ClientModulesResponse)
def fetch_client_modules(
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    result = get_client_modules(current_client.id, db)

    if not result:
        raise HTTPException(status_code=404, detail="Modules not initialized")

    return result


# POST (FIRST TIME SAVE)
@router.post("", response_model=ClientModulesResponse)
def create_client_modules(
    payload: ClientModulesUpsertRequest,
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    try:
        return upsert_client_modules(
            client_id=current_client.id,
            selected_module_ids=payload.selected_module_ids,
            comment=payload.comment,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# PUT (UPDATE SELECTION)
@router.put("", response_model=ClientModulesResponse)
def update_client_modules(
    payload: ClientModulesUpsertRequest,
    current_client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    try:
        return upsert_client_modules(
            client_id=current_client.id,
            selected_module_ids=payload.selected_module_ids,
            comment=payload.comment,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))