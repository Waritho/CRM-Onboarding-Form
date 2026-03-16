from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.client_user import ClientUser
from app.schemas.client_user_schema import ClientUserCreate, ClientUserUpdate


def get_users(client_id: int, db: Session):
    try:
        users = db.query(ClientUser).filter(
            ClientUser.client_id == client_id,
            ClientUser.is_active == True
        ).all()

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found"
            )

        return users

    except HTTPException:
        # Re-raise HTTP exceptions so FastAPI can handle them
        raise

    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

def create_user(client_id: int, user_data: ClientUserCreate, db: Session):
    existing_user = db.query(ClientUser).filter(ClientUser.email == user_data.email).first()
    if existing_user:
        if existing_user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
        else:
            existing_user.is_active = True
            existing_user.client_id = client_id
            existing_user.can_write = user_data.can_write
            db.commit()
            db.refresh(existing_user)
            return existing_user

    new_user = ClientUser(
        client_id=client_id,
        email=user_data.email,
        can_write=user_data.can_write,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(client_id: int, user_id: int, user_data: ClientUserUpdate, db: Session):
    user = db.query(ClientUser).filter(
        ClientUser.id == user_id, 
        ClientUser.client_id == client_id,
        ClientUser.is_active == True
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.can_write = user_data.can_write
    db.commit()
    db.refresh(user)
    return user

def delete_user(client_id: int, user_id: int, db: Session):
    user = db.query(ClientUser).filter(
        ClientUser.id == user_id, 
        ClientUser.client_id == client_id,
        ClientUser.is_active == True
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    db.commit()
    return {"message": "User deleted successfully"}