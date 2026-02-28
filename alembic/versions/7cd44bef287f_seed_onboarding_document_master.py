"""seed onboarding document master

Revision ID: 7cd44bef287f
Revises: 2d141fd2099c
Create Date: 2026-02-28 16:56:49.426224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean


# revision identifiers, used by Alembic.
revision: str = '7cd44bef287f'
down_revision: Union[str, Sequence[str], None] = '2d141fd2099c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    onboarding_document_master = table(
        "onboarding_document_master",
        column("code", String),
        column("name", String),
        column("is_mandatory", Boolean),
    )

    op.bulk_insert(
        onboarding_document_master,
        [
            {"code": "logo", "name": "Logo", "is_mandatory": True},
            {"code": "theme_image", "name": "Theme Image", "is_mandatory": True},
            {"code": "incorporation_certificate", "name": "Company Incorporation Certificate", "is_mandatory": True},
            {"code": "gst_certificate", "name": "GST Certificate", "is_mandatory": True},
            {"code": "pan_card", "name": "PAN Card", "is_mandatory": True},
            {"code": "photo_id", "name": "Photo ID Proof of Signatory", "is_mandatory": True},
            {"code": "purchase_order", "name": "Purchase Order", "is_mandatory": True},
            {"code": "noc_data_storage", "name": "NOC for Secured Data Storage", "is_mandatory": True},
            {"code": "service_agreement", "name": "Service Agreement", "is_mandatory": True},
        ]
    )


def downgrade():
    op.execute("DELETE FROM onboarding_document_master")
