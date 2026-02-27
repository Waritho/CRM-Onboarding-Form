from sqlalchemy import Column,Integer,DateTime,ForeignKey,CheckConstraint,func
from app.database import Base


class ClientTentativeCounts(Base):
    __tablename__ = "client_tentative_counts"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer,ForeignKey("clients.id", ondelete="CASCADE"),unique=True,nullable=False)

    lead_intake = Column(Integer,nullable=False,server_default="0")

    application_count = Column(Integer,nullable=False,server_default="0")

    raw_data_count = Column(Integer,nullable=False,server_default="0")

    crm_count = Column(Integer,nullable=False,server_default="0")

    widget_count = Column(Integer,nullable=False,server_default="0")

    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

    __table_args__ = (
        CheckConstraint("lead_intake >= 0", name="check_lead_intake_non_negative"),
        CheckConstraint("application_count >= 0", name="check_application_non_negative"),
        CheckConstraint("raw_data_count >= 0", name="check_raw_data_non_negative"),
        CheckConstraint("crm_count >= 0", name="check_crm_non_negative"),
        CheckConstraint("widget_count >= 0", name="check_widget_non_negative"),
    )