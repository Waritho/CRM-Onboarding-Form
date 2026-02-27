from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint, func
from app.database import Base


class ClientModule(Base):
    __tablename__ = "client_modules"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="RESTRICT"), nullable=False)

    is_enabled = Column(Boolean, nullable=False, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("client_id", "module_id", name="uq_client_module"),
    )