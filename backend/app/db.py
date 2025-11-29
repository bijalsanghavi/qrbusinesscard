import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Start Postgres (docker) and set DATABASE_URL in backend/.env")

# Fix Railway's postgresql:// to use psycopg (psycopg3) instead of psycopg2
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Add connection parameters for database stability
# Different databases support different connection parameters
engine_args = {
    "pool_pre_ping": True,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_timeout": 30,
}

# Add PostgreSQL-specific connection parameters
if DATABASE_URL.startswith("postgresql"):
    engine_args["connect_args"] = {
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30 second timeout
    }
elif DATABASE_URL.startswith("sqlite"):
    # SQLite supports check_same_thread parameter
    engine_args["connect_args"] = {
        "check_same_thread": False
    }

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
