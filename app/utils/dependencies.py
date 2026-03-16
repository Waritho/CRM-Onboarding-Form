from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.utils.jwt_handler import decode_token
from app.database import get_db
from app.models.client import Client
from app.models.client_user import ClientUser

security = HTTPBearer()


def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token" 
            )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    client_id = payload.get("client_id")

    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client, db

def get_primary_client_only(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    client, db_session = get_current_client(credentials, db)
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("role") != "primary":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Only the primary client can perform this action."
        )
        
    return client, db_session

def require_unsubmitted_form(
    current_client = Depends(get_current_client)
):
    client, db = current_client
    if client.is_submitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Form has already been submitted and cannot be modified."
        )
    return client, db

def require_write_access(
    current_client = Depends(require_unsubmitted_form),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    client, db = current_client
    token = credentials.credentials
    payload = decode_token(token)
    
    role = payload.get("role", "primary")
    if role == "primary":
        return client, db
        
    email = payload.get("email")
    if email:
        sub_user = db.query(ClientUser).filter(ClientUser.email == email).first()
        if sub_user and not sub_user.can_write:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to make changes to this form."
            )
            
    return client, db

def require_primary_unsubmitted_form(
    current_client = Depends(get_primary_client_only)
):
    client, db = current_client
    if client.is_submitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Form has already been submitted and cannot be modified."
        )
    return client, db