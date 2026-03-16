from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.utils.dependencies import get_primary_client_only
from app.schemas.client_user_schema import ClientUserResponse, ClientUserCreate, ClientUserUpdate
from app.services.client_user_service import get_users, create_user, update_user, delete_user

router = APIRouter(prefix="/client/users", tags=["Client Users"])

@router.get("", response_model=List[ClientUserResponse])
def list_sub_users(
    current_client = Depends(get_primary_client_only)
):
    client, db = current_client
    return get_users(client.id, db)

@router.post("", response_model=ClientUserResponse, status_code=status.HTTP_201_CREATED)
def create_new_sub_user(
    data: ClientUserCreate,
    current_client = Depends(get_primary_client_only)
):
    client, db = current_client
    return create_user(client.id, data, db)

@router.put("/{user_id}", response_model=ClientUserResponse)
def update_sub_user(
    user_id: int,
    data: ClientUserUpdate,
    current_client = Depends(get_primary_client_only)
):
    client, db = current_client
    return update_user(client.id, user_id, data, db)

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_sub_user(
    user_id: int,
    current_client = Depends(get_primary_client_only)
):
    client, db = current_client
    return delete_user(client.id, user_id, db)
