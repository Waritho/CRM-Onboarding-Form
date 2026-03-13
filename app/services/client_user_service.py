from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.client_user import ClientUser


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