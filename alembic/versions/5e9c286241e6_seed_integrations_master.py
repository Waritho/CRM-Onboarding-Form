"""seed integrations master

Revision ID: 5e9c286241e6
Revises: e2765f284028
Create Date: 2026-02-25 16:54:55.273761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e9c286241e6'
down_revision: Union[str, Sequence[str], None] = 'e2765f284028'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    integrations_table = sa.table(
        "integrations_master",
        sa.column("name", sa.String)
    )

    op.bulk_insert(
        integrations_table,
        [
            {"name": "SMS"},
            {"name": "WhatsApp"},
            {"name": "Email"},
            {"name": "Telephony"},
            {"name": "Third Party Integrations"},
            {"name": "GD/PI Process"},
        ]
    )


def downgrade():
    op.execute(
        "DELETE FROM integrations_master WHERE name IN "
        "('SMS','WhatsApp','Email','Telephony','Third Party Integrations','GD/PI Process')"
    )
