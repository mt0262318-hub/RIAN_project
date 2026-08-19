import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL connection URL from environment or default docker setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://rian_user:rian_password@db:5432/rian_db"
)

# Optimized Engine with connection pooling and pre-ping for multi-user stability
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Keeps 20 permanent connections open in the pool
    max_overflow=10,  # Allows up to 10 additional temporary connections during peak load
    pool_pre_ping=True,  # Automatically detects and drops stale connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session in FastAPI endpoints
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()