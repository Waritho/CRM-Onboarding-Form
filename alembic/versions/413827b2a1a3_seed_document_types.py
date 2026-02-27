"""seed document types

Revision ID: 413827b2a1a3
Revises: cc6144fd1f34
Create Date: 2026-02-26 11:21:36.078068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '413827b2a1a3'
down_revision: Union[str, Sequence[str], None] = 'cc6144fd1f34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    document_table = sa.table(
        "document_types",
        sa.column("name", sa.String)
    )

    op.bulk_insert(
        document_table,
        [
            {"name": "Previous Year Lead Dump"},
            {"name": "Sample Report 1"},
            {"name": "Sample Report 2"},
            {"name": "Miscellaneous Documents"}
        ]
    )


def downgrade():
    op.execute(
        "DELETE FROM document_types WHERE name IN "
        "('Previous Year Lead Dump','Sample Report 1','Sample Report 2','Miscellaneous Documents')"
    )