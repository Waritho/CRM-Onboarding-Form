from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class OnboardingDocumentMaster(Base):
    __tablename__ = "onboarding_document_master"

    id = Column(Integer, primary_key=True)

    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    is_mandatory = Column(Boolean, nullable=False, server_default="false")