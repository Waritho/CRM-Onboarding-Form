from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.client import Client


def submit_form(client: Client, db: Session):
    if client.is_submitted:
        raise HTTPException(
            status_code=400,
            detail="Form has already been submitted."
        )

    client.is_submitted = True
    db.commit()
    db.refresh(client)

    return {"message": "Form submitted successfully. No further changes allowed."}


def get_submission_status(client: Client):
    return {"is_submitted": client.is_submitted}
