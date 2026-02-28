from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Index
from app.database import Base


class ClientOnboardingDocument(Base):
    __tablename__ = "client_onboarding_documents"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False
    )

    document_id = Column(
        Integer,
        ForeignKey("onboarding_document_master.id", ondelete="CASCADE"),
        nullable=False
    )

    file_url = Column(String, nullable=False)

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index("idx_client_document", "client_id"),
        Index("uq_client_document", "client_id", "document_id", unique=True),
    )