"""create_client_domain_config

Revision ID: dd2940939e71
Revises: 27b4c5f4f9ba
Create Date: 2026-02-28 16:50:59.999701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd2940939e71'
down_revision: Union[str, Sequence[str], None] = '27b4c5f4f9ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.create_table(
        "client_domain_config",

        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "client_id",
            sa.Integer(),
            sa.ForeignKey("clients.id", ondelete="CASCADE"),
            nullable=False,
            unique=True
        ),

        sa.Column("main_domain", sa.String(), nullable=False),
        sa.Column("subdomain", sa.String(), nullable=False),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),

        sa.UniqueConstraint("main_domain", name="uq_main_domain"),
        sa.UniqueConstraint("subdomain", name="uq_subdomain"),
    )

    op.create_index(
        "idx_domain_client_id",
        "client_domain_config",
        ["client_id"]
    )

    op.create_index(
        "idx_domain_main",
        "client_domain_config",
        ["main_domain"]
    )

    op.create_index(
        "idx_domain_sub",
        "client_domain_config",
        ["subdomain"]
    )


def downgrade():

    op.drop_index("idx_domain_sub", table_name="client_domain_config")
    op.drop_index("idx_domain_main", table_name="client_domain_config")
    op.drop_index("idx_domain_client_id", table_name="client_domain_config")

    op.drop_table("client_domain_config")
