from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,func,Index,CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class ClientPaymentProvider(Base):
    __tablename__ = "client_payment_provider"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False
    )

    provider = Column(String, nullable=False)

    is_enabled = Column(Boolean, nullable=False, server_default="true")

    credentials = Column(JSONB, nullable=False)

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
        Index("idx_payment_client", "client_id"),
        Index("uq_client_provider", "client_id", "provider", unique=True),
        CheckConstraint(
            "provider IN ('razorpay','easy_buzz','ezypay','hdfc','payu')",
            name="chk_payment_provider"
        ),
    )