from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.utils.dependencies import get_primary_client_only
from app.schemas.client_user_schema import ClientUserResponse
from app.services.client_user_service import get_users

router = APIRouter(prefix="/client/users", tags=["Client Users"])

@router.get("", response_model=List[ClientUserResponse])
def list_sub_users(
    current_client = Depends(get_primary_client_only)
):
    client, db = current_client
    return get_users(client.id, db)
