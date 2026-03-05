from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, text
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    is_submitted = Column(Boolean, default=False, server_default=text('false'), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())