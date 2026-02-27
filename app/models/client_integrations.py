from sqlalchemy import Column,Integer,Boolean,DateTime,ForeignKey,UniqueConstraint,func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class ClientIntegrations(Base):
    __tablename__ = "client_integrations"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False
    )

    integration_id = Column(
        Integer,
        ForeignKey("integrations_master.id", ondelete="RESTRICT"),
        nullable=False
    )

    is_enabled = Column(
        Boolean,
        nullable=False,
        server_default="false"
    )

    # dynamic config per integration
    config = Column(
        JSONB,
        nullable=False,
        server_default="{}"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "integration_id",
            name="unique_client_integration"
        ),
    )