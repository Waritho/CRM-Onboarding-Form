from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# DATABASE ENGINE

engine = create_engine(
    settings.DATABASE_URL,  
    future=True
)

# SESSION LOCAL

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# BASE MODEL (ALL MODELS INHERIT)

Base = declarative_base()

# DB DEPENDENCY (IMPORTANT)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()