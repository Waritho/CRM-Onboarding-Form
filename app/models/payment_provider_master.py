from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class PaymentProviderMaster(Base):
    __tablename__ = "payment_provider_master"

    id = Column(Integer, primary_key=True, index=True)

    # e.g., "razorpay"
    code = Column(String, unique=True, nullable=False)

    # e.g., "Razorpay"
    display_name = Column(String, nullable=False)

    # e.g., ["razorpay_api_key", "razorpay_secret"]
    required_fields = Column(JSONB, nullable=False)

    is_active = Column(Boolean, nullable=False, server_default="true")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
