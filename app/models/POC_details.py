from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class ClientPOC(Base):
    __tablename__ = "client_pocs"

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey("clients.id" , ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    mobile = Column(String, nullable=False)

    is_primary = Column(Boolean, default=False, nullable=False)

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
    UniqueConstraint('client_id', 'email', name='uq_client_email'), # Same client cannot have same email twice.
    UniqueConstraint('client_id', 'mobile', name='uq_client_mobile'), # Same client cannot have same mobile twice.
)