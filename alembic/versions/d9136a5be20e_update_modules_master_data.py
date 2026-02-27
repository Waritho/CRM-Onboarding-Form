"""update modules master data

Revision ID: d9136a5be20e
Revises: 06803e3ffba8
Create Date: 2026-02-26 13:23:57.294852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9136a5be20e'
down_revision: Union[str, Sequence[str], None] = '06803e3ffba8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # completely wipe table safely
    op.execute("TRUNCATE TABLE modules RESTART IDENTITY CASCADE")

    modules_table = sa.table(
        "modules",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        modules_table,
        [
            {"id": 1, "name": "QA Manager", "is_active": True},
            {"id": 2, "name": "Data segment Manager", "is_active": True},
            {"id": 3, "name": "Communication", "is_active": True},
            {"id": 4, "name": "Application Manager", "is_active": True},
            {"id": 5, "name": "Lead Manager", "is_active": True},
            {"id": 6, "name": "Campaign Manager", "is_active": True},
            {"id": 7, "name": "Interview Manager", "is_active": True},
            {"id": 8, "name": "User Access Control", "is_active": True},
            {"id": 9, "name": "Report&Analytics", "is_active": True},
            {"id": 10, "name": "Automation Manager", "is_active": True},
            {"id": 11, "name": "Template Manager", "is_active": True},
            {"id": 12, "name": "Offline Data", "is_active": True},
            {"id": 13, "name": "Resources", "is_active": True},
        ],
    )


def downgrade():
    op.execute("TRUNCATE TABLE modules RESTART IDENTITY CASCADE")