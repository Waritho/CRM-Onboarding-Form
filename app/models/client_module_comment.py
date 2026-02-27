from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func
from app.database import Base


class ClientModuleComment(Base):
    __tablename__ = "client_module_comments"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    comment = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())