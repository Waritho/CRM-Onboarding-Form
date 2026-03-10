"""remove result mode fields from ug and pg details

Revision ID: 1bcc9b46ab77
Revises: a7ec8684ee1d
Create Date: 2026-03-10 16:09:56.832605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bcc9b46ab77'
down_revision: Union[str, Sequence[str], None] = 'a7ec8684ee1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Delete obsolete result mode fields."""
    connection = op.get_bind()

    # 1. DELETE from master table
    connection.execute(
        sa.text("DELETE FROM form_fields_master WHERE field_key IN ('ug_result_mode', 'pg_result_mode')")
    )

    # 2. DELETE corresponding client configurations to keep DB clean
    connection.execute(
        sa.text("DELETE FROM client_form_fields WHERE field_id NOT IN (SELECT id FROM form_fields_master)")
    )


def downgrade() -> None:
    """Downgrade not supported for data deletion."""
    pass
