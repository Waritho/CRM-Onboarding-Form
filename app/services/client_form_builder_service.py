from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.client_form_builder import (
    ClientFormSection,
    ClientFormField,
    FormFieldMaster,
    FormSection
)

from app.schemas.client_form_builder_schema import (
    FormConfigCreate,
    FormUIConfigResponse,
)

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

                # If the parent section is disabled, force this field off too
                is_enabled = field.is_enabled if section.is_enabled else False

                field_obj = ClientFormField(
                    client_id=client_id,
                    field_id=field.field_id,
                    is_enabled=is_enabled,
                    is_required=False  # Not used in this project; column kept for schema compat
                )

                db.add(field_obj)

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# GET FORM CONFIG — FULL UI HYDRATION (Master data + client state merged)

def get_form_config(db: Session, client_id: int) -> dict:
    """
    Returns ALL active sections and their fields from the master tables,
    with per-client is_enabled state overlaid on top.

    A brand-new client will see every section and field defaulted to
    is_enabled=False, which is the safe default.
    """

    # 1. Fetch all active master sections ordered by sort order
    master_sections = (
        db.query(FormSection)
        .filter(FormSection.is_active == True)
        .order_by(FormSection.default_sort_order)
        .all()
    )

    # 2. Fetch all active master fields ordered by sort order
    master_fields = (
        db.query(FormFieldMaster)
        .filter(FormFieldMaster.is_active == True)
        .order_by(FormFieldMaster.default_sort_order)
        .all()
    )

    # 3. Build lookup maps for client-specific state — O(1) access
    #    Key: section_id → ClientFormSection row
    client_section_map = {
        row.section_id: row
        for row in db.query(ClientFormSection)
                     .filter(ClientFormSection.client_id == client_id)
                     .all()
    }

    #    Key: field_id → ClientFormField row
    client_field_map = {
        row.field_id: row
        for row in db.query(ClientFormField)
                     .filter(ClientFormField.client_id == client_id)
                     .all()
    }

    # 4. Group master fields by section_id for easy iteration
    fields_by_section: dict = {}
    for field in master_fields:
        fields_by_section.setdefault(field.section_id, []).append(field)

    # 5. Merge master sections + client state
    sections_out = []

    for ms in master_sections:
        client_section = client_section_map.get(ms.id)

        # Merge per-field state
        fields_out = []
        for mf in fields_by_section.get(ms.id, []):
            client_field = client_field_map.get(mf.id)
            fields_out.append({
                "field_id":   mf.id,
                "field_key":  mf.field_key,
                "label":      mf.label,
                "field_type": mf.field_type,
                "sort_order": mf.default_sort_order,
                "is_enabled":  client_field.is_enabled if client_field else False,
            })

        sections_out.append({
            "section_id":   ms.id,
            "code":         ms.code,
            "name":         ms.name,
            "is_repeatable": ms.is_repeatable,
            "sort_order":   ms.default_sort_order,
            "is_enabled":   client_section.is_enabled   if client_section else False,
            "comment_text": client_section.comment_text if client_section else None,
            "fields":       fields_out,
        })

    return {
        "client_id": client_id,
        "sections":  sections_out,
    }
