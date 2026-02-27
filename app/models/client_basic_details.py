from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ClientBasicDetails(Base):
    __tablename__ = "client_basic_details"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(Integer, ForeignKey("clients.id" , ondelete="CASCADE"), unique=True)

    institution_name = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    address = Column(Text)
    website = Column(String)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP,server_default=func.now(),onupdate=func.now())