# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Define where the database file should live locally
SQLALCHEMY_DATABASE_URL = "sqlite:///./news_digest.db"

# 2. Create the engine. (check_same_thread is only needed for SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a Session factory. This gives us database connections.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Base class that our models will inherit from
Base = declarative_base()