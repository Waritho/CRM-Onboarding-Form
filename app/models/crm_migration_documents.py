from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Text,
    func
)
from app.database import Base


class CRMMigrationDocument(Base):
    __tablename__ = "crm_migration_documents"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False
    )

    document_type_id = Column(
        Integer,
        ForeignKey("document_types.id", ondelete="RESTRICT"),
        nullable=False
    )

    file_path = Column(
        Text,
        nullable=False
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "document_type_id",
            name="unique_client_document"
        ),
    )