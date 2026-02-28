"""add comment_text to client_form_sections

Revision ID: 091d9882ed9c
Revises: 94f8c4c9883c
Create Date: 2026-02-28 14:17:34.219508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '091d9882ed9c'
down_revision: Union[str, Sequence[str], None] = '94f8c4c9883c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
