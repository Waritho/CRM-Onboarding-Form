from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.client_form_builder import (
    ClientFormSection,
    ClientFormField,
    FormFieldMaster,
    FormSection
)

from app.schemas.client_form_builder_schema import FormConfigCreate



# UPSERT FORM CONFIG (FULL REPLACE)


def upsert_form_config(
    db: Session,
    client_id: int,
    payload: FormConfigCreate
):
    try:

        # DELETE OLD CONFIG
        db.query(ClientFormField).filter(
            ClientFormField.client_id == client_id
        ).delete()

        db.query(ClientFormSection).filter(
            ClientFormSection.client_id == client_id
        ).delete()

        db.flush()

        # PROCESS NEW CONFIG

        for section in payload.sections:

            # Validate section exists
            master_section = db.query(FormSection).filter(
                FormSection.id == section.section_id
            ).first()

            if not master_section:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid section_id {section.section_id}"
                )

            # Rule: If enabled → must have at least 1 enabled field
            if section.is_enabled:
                enabled_fields = [
                    f for f in section.fields if f.is_enabled
                ]

                if len(enabled_fields) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Section {section.section_id} must have at least one enabled field."
                    )

            # Create section record
            section_obj = ClientFormSection(
                client_id=client_id,
                section_id=section.section_id,
                is_enabled=section.is_enabled,
                comment_text=section.comment_text if section.is_enabled else None
            )

            db.add(section_obj)
            db.flush()


            # Insert field configs

            for field in section.fields:

                master_field = db.query(FormFieldMaster).filter(
                    FormFieldMaster.id == field.field_id,
                    FormFieldMaster.section_id == section.section_id
                ).first()

                if not master_field:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Field {field.field_id} does not belong to section {section.section_id}"
                    )

                # Enforce rules
                if not section.is_enabled:
                    is_enabled = False
                    is_required = False
                else:
                    is_enabled = field.is_enabled
                    is_required = field.is_required if field.is_enabled else False

                field_obj = ClientFormField(
                    client_id=client_id,
                    field_id=field.field_id,
                    is_enabled=is_enabled,
                    is_required=is_required
                )

                db.add(field_obj)

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# GET FORM CONFIG (NESTED RESPONSE)

def get_form_config(db: Session, client_id: int):

    sections = db.query(ClientFormSection).filter(
        ClientFormSection.client_id == client_id
    ).all()

    fields = db.query(ClientFormField).filter(
        ClientFormField.client_id == client_id
    ).all()

    # Build map: section_id → fields
    section_field_map = {}

    for field in fields:
        master_field = db.query(FormFieldMaster).filter(
            FormFieldMaster.id == field.field_id
        ).first()

        if not master_field:
            continue

        section_field_map.setdefault(master_field.section_id, []).append({
            "id": field.id,
            "field_id": field.field_id,
            "is_enabled": field.is_enabled,
            "is_required": field.is_required
        })

    response_sections = []

    for section in sections:
        response_sections.append({
            "id": section.id,
            "section_id": section.section_id,
            "is_enabled": section.is_enabled,
            "comment_text": section.comment_text,
            "fields": section_field_map.get(section.section_id, [])
        })

    return {
        "sections": response_sections
    }