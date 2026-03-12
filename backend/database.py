
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------------------------------
# DATABASE URL
# ---------------------------------------------------
# Priority:
# 1. Use DATABASE_URL from .env (for production)
# 2. Fallback to SQLite for local development
# ---------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sidequest.db")

# ---------------------------------------------------
# Engine Configuration
# ---------------------------------------------------

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

# ---------------------------------------------------
# Session
# ---------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ---------------------------------------------------
# Base Model
# ---------------------------------------------------

Base = declarative_base()

# ---------------------------------------------------
# Dependency for FastAPI
# ---------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()