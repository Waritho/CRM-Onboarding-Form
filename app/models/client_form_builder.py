from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Index,
    Text
)
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base


# GLOBAL: FORM SECTIONS

class FormSection(Base):
    __tablename__ = "form_sections"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)

    default_sort_order = Column(Integer, nullable=False)

    is_repeatable = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    fields = relationship(
        "FormFieldMaster",
        back_populates="section",
        cascade="all, delete"
    )


# GLOBAL: FORM FIELDS MASTER

class FormFieldMaster(Base):
    __tablename__ = "form_fields_master"

    id = Column(Integer, primary_key=True, index=True)

    section_id = Column(
        Integer,
        ForeignKey("form_sections.id", ondelete="CASCADE"),
        nullable=False
    )

    field_key = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)
    field_type = Column(String, nullable=False)

    default_sort_order = Column(Integer, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    section = relationship("FormSection", back_populates="fields")


# TENANT: CLIENT SECTION CONFIG

class ClientFormSection(Base):
    __tablename__ = "client_form_sections"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False
    )

    section_id = Column(
        Integer,
        ForeignKey("form_sections.id", ondelete="CASCADE"),
        nullable=False
    )

    is_enabled = Column(Boolean, default=False)

    # 🔥 IMPORTANT FIX
    comment_text = Column(Text, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "section_id",
            name="uq_client_section_config"
        ),
        Index("idx_client_form_sections_client_id", "client_id"),
    )


# TENANT: CLIENT FIELD CONFIG

class ClientFormField(Base):
    __tablename__ = "client_form_fields"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False
    )

    field_id = Column(
        Integer,
        ForeignKey("form_fields_master.id", ondelete="CASCADE"),
        nullable=False
    )

    is_enabled = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "field_id",
            name="uq_client_field_config"
        ),
        Index("idx_client_form_fields_client_id", "client_id"),
    )