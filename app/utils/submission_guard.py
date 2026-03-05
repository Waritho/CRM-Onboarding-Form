from fastapi import HTTPException, status

def ensure_not_submitted(current_client_tuple):
    """
    Dependency guard: blocks any write operation
    if the client has already submitted.
    Call AFTER get_current_client.
    """
    client, db = current_client_tuple
    if client.is_submitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Form already submitted. No changes allowed."
        )
    return client, db
