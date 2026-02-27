from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.integrations_master import IntegrationsMaster
from app.models.client_integrations import ClientIntegrations


# GET FULL INTEGRATIONS STATE
def get_client_integrations(client_id: int, db: Session):

    master_integrations = db.query(IntegrationsMaster).filter(
        IntegrationsMaster.is_active == True
    ).all()

    client_rows = db.query(ClientIntegrations).filter(
        ClientIntegrations.client_id == client_id
    ).all()

    client_map = {
        row.integration_id: row for row in client_rows
    }

    response = []

    for integration in master_integrations:

        client_data = client_map.get(integration.id)

        if client_data:
            response.append({
                "integration_id": integration.id,
                "name": integration.name,
                "is_enabled": client_data.is_enabled,
                "config": client_data.config or {}
            })
        else:
            response.append({
                "integration_id": integration.id,
                "name": integration.name,
                "is_enabled": False,
                "config": {}
            })

    return response


# UPSERT FULL FORM
def upsert_client_integrations(client_id: int, data, db: Session):

    try:
        for item in data:

            record = db.query(ClientIntegrations).filter(
                ClientIntegrations.client_id == client_id,
                ClientIntegrations.integration_id == item.integration_id
            ).first()

            # CREATE
            if not record:
                new_record = ClientIntegrations(
                    client_id=client_id,
                    integration_id=item.integration_id,
                    is_enabled=item.is_enabled,
                    config=item.config or {}
                )
                db.add(new_record)

            # UPDATE
            else:
                record.is_enabled = item.is_enabled
                record.config = item.config or {}

        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")

    return {"message": "Integrations saved successfully"}