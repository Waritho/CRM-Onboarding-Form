from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base


class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)

    is_active = Column(
        Boolean,
        nullable=False,
        server_default="true"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )