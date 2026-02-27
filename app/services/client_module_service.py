from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.module_master import Module
from app.models.client_modules import ClientModule
from app.models.client_module_comment import ClientModuleComment


# -----------------------------
# GET CLIENT MODULES
# -----------------------------
def get_client_modules(client_id: int, db: Session):

    # Check if client has module rows
    existing = (
        db.query(ClientModule)
        .filter(ClientModule.client_id == client_id)
        .all()
    )

    if not existing:
        return None  # Explicitly no auto-create

    # Fetch module master
    modules = db.query(Module).filter(Module.is_active == True).all()

    # Build map for fast lookup
    enabled_map = {m.module_id: m.is_enabled for m in existing}

    result = []
    for module in modules:
        result.append({
            "module_id": module.id,
            "module_name": module.name,
            "is_enabled": enabled_map.get(module.id, False)
        })

    # Fetch comment
    comment_obj = (
        db.query(ClientModuleComment)
        .filter(ClientModuleComment.client_id == client_id)
        .first()
    )

    return {
        "modules": result,
        "comment": comment_obj.comment if comment_obj else None
    }


# -----------------------------
# UPSERT CLIENT MODULES
# -----------------------------
def upsert_client_modules(client_id: int, selected_module_ids: list[int], comment: str | None, db: Session):

    # Validate module IDs exist
    valid_modules = db.query(Module.id).all()
    valid_ids = {m.id for m in valid_modules}

    for mid in selected_module_ids:
        if mid not in valid_ids:
            raise ValueError(f"Invalid module id: {mid}")

    # Check if rows exist
    existing_rows = (
        db.query(ClientModule)
        .filter(ClientModule.client_id == client_id)
        .all()
    )

    # If first time → initialize all modules
    if not existing_rows:
        modules = db.query(Module).filter(Module.is_active == True).all()

        for module in modules:
            db.add(
                ClientModule(
                    client_id=client_id,
                    module_id=module.id,
                    is_enabled=False
                )
            )

        db.flush()  # create rows but don't commit yet

        existing_rows = (
            db.query(ClientModule)
            .filter(ClientModule.client_id == client_id)
            .all()
        )

    # Reset all to False
    for row in existing_rows:
        row.is_enabled = False

    # Enable selected
    for row in existing_rows:
        if row.module_id in selected_module_ids:
            row.is_enabled = True

    # Upsert comment
    comment_obj = (
        db.query(ClientModuleComment)
        .filter(ClientModuleComment.client_id == client_id)
        .first()
    )

    if comment_obj:
        comment_obj.comment = comment
    else:
        db.add(
            ClientModuleComment(
                client_id=client_id,
                comment=comment
            )
        )

    db.commit()

    return get_client_modules(client_id, db)