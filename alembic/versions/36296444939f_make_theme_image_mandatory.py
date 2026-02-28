"""make theme_image mandatory

Revision ID: 36296444939f
Revises: 7cd44bef287f
Create Date: 2026-02-28 17:00:31.033173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36296444939f'
down_revision: Union[str, Sequence[str], None] = '7cd44bef287f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        UPDATE onboarding_document_master
        SET is_mandatory = TRUE
        WHERE code = 'theme_image'
    """)


def downgrade():
    op.execute("""
        UPDATE onboarding_document_master
        SET is_mandatory = FALSE
        WHERE code = 'theme_image'
    """)