import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "api-postgresql:5432/api_service")
SQLALCHEMY_DATABASE_USER = os.environ.get("DATABASE_USER", "api_service")
SQLALCHEMY_DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "api_service")

engine = create_engine(f"postgresql://{SQLALCHEMY_DATABASE_USER}:{SQLALCHEMY_DATABASE_PASSWORD}@{SQLALCHEMY_DATABASE_URL}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
