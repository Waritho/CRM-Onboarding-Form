from fastapi import APIRouter, Depends, HTTPException
from app.utils.dependencies import get_current_client, require_write_access
from app.services.client_submission_service import (
    submit_form,
    get_submission_status
)

router = APIRouter(prefix="/client", tags=["Client Submission"])


# SUBMIT FORM (one-way latch)
@router.post("/submit")
def submit_client_form(
    current_client=Depends(require_write_access)
):
    current_client, db = current_client
    return submit_form(current_client, db)


# GET SUBMISSION STATUS
@router.get("/submission-status")
def check_submission_status(
    current_client=Depends(get_current_client)
):
    current_client, db = current_client
    return get_submission_status(current_client)
