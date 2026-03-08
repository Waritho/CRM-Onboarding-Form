from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from psycopg2.extensions import register_adapter, adapt
from pydantic import HttpUrl
from app.config import settings


# Register adapter so psycopg2 can handle Pydantic's HttpUrl type
def adapt_httpurl(url):
    return adapt(str(url))

register_adapter(HttpUrl, adapt_httpurl)

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