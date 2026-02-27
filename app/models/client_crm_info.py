from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,func
from app.database import Base


class ClientCRMInfo(Base):
    __tablename__ = "client_crm_info"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer,ForeignKey("clients.id", ondelete="CASCADE"),unique=True,nullable=False)

    using_crm = Column(Boolean, nullable=False, server_default="false")

    crm_name = Column(String, nullable=True)

    want_data_migration = Column(Boolean,nullable=False,server_default="false")

    previous_crm_name = Column(String, nullable=True)

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