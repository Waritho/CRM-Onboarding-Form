from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from app.database import Base


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())