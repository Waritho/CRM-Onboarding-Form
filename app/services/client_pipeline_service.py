from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.client_pipeline import (
    ClientLeadStage,
    ClientLeadSubStage,
    ClientLeadTag
)

from app.schemas.client_pipeline_schema import (
    PipelineConfigCreate
)


# UPSERT PIPELINE CONFIG (FULL REPLACE)
def upsert_pipeline_config(
    db: Session,
    client_id: int,
    payload: PipelineConfigCreate
):
    try:
        # DELETE OLD DATA (FULL RESET)
        db.query(ClientLeadSubStage).filter(
            ClientLeadSubStage.client_id == client_id
        ).delete()

        db.query(ClientLeadStage).filter(
            ClientLeadStage.client_id == client_id
        ).delete()

        db.query(ClientLeadTag).filter(
            ClientLeadTag.client_id == client_id
        ).delete()

        db.flush()

        # INSERT STAGES + SUBSTAGES
        for stage in payload.stages:
            stage_obj = ClientLeadStage(
                client_id=client_id,
                name=stage.name.strip(),
                position=stage.position,
                comment=stage.comment,
                is_enabled=stage.is_enabled
            )
            db.add(stage_obj)
            db.flush()  # get stage id

            # sub stages
            for sub in stage.sub_stages:
                sub_obj = ClientLeadSubStage(
                    client_id=client_id,
                    stage_id=stage_obj.id,
                    name=sub.name.strip(),
                    position=sub.position,
                    is_enabled=sub.is_enabled
                )
                db.add(sub_obj)

        # INSERT TAGS
        for tag in payload.tags:
            tag_obj = ClientLeadTag(
                client_id=client_id,
                name=tag.name.strip(),
                is_enabled=tag.is_enabled
            )
            db.add(tag_obj)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# GET PIPELINE CONFIG
def get_pipeline_config(db: Session, client_id: int):
    
    stages = (
        db.query(ClientLeadStage)
        .options(joinedload(ClientLeadStage.sub_stages))
        .filter(ClientLeadStage.client_id == client_id)
        .order_by(ClientLeadStage.position)
        .all()
    )

    tags = (
        db.query(ClientLeadTag)
        .filter(ClientLeadTag.client_id == client_id)
        .all()
    )

    return {
        "stages": stages,
        "tags": tags
    }