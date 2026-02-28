from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint, Index
from app.database import Base


class ClientDomainConfig(Base):
    __tablename__ = "client_domain_config"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    main_domain = Column(String, nullable=False, unique=True)
    subdomain = Column(String, nullable=False, unique=True)

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
        Index("idx_domain_client_id", "client_id"),
        Index("idx_domain_main", "main_domain"),
        Index("idx_domain_sub", "subdomain"),
    )