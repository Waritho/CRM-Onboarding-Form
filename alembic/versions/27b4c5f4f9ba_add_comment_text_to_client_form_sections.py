"""add comment_text to client_form_sections

Revision ID: 27b4c5f4f9ba
Revises: 091d9882ed9c
Create Date: 2026-02-28 14:20:17.161129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27b4c5f4f9ba'
down_revision: Union[str, Sequence[str], None] = '091d9882ed9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "client_form_sections",
        sa.Column("comment_text", sa.Text(), nullable=True)
    )


def downgrade():
    op.drop_column("client_form_sections", "comment_text")
