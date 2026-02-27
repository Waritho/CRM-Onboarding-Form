from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from app.database import Base


# LEAD STAGES
class ClientLeadStage(Base):
    __tablename__ = "client_lead_stages"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False)

    comment = Column(Text, nullable=True)

    is_enabled = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    sub_stages = relationship(
        "ClientLeadSubStage",
        back_populates="stage",
        cascade="all, delete"
    )

    __table_args__ = (
        UniqueConstraint("client_id", "name", name="uq_stage_name_per_client"),
    )


# SUB STAGES
class ClientLeadSubStage(Base):
    __tablename__ = "client_lead_sub_stages"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    stage_id = Column(Integer, ForeignKey("client_lead_stages.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False)

    is_enabled = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    stage = relationship("ClientLeadStage", back_populates="sub_stages")

    __table_args__ = (
        UniqueConstraint("client_id", "stage_id", "name", name="uq_substage_per_stage"),
    )


# TAGS
class ClientLeadTag(Base):
    __tablename__ = "client_lead_tags"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("client_id", "name", name="uq_tag_per_client"),
    )