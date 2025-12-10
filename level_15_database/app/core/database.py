"""
Database Connection & Session Management
=========================================
This module sets up SQLAlchemy for FastAPI.

Key Components:
1. engine - Database connection
2. SessionLocal - Session factory
3. Base - Declarative base for models
4. get_db - Dependency for database sessions
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ============================================================
# CONCEPT 1: Create Database Engine
# ============================================================
# The engine is the starting point for SQLAlchemy
# It maintains a pool of connections to the database

# For SQLite, we need connect_args to allow multi-threading
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only for SQLite
    # For PostgreSQL/MySQL, remove connect_args
)

# For PostgreSQL:
# engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)


# ============================================================
# CONCEPT 2: Create Session Factory
# ============================================================
# SessionLocal is a factory that creates new database sessions
# Each request gets its own session

SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit (we control transactions)
    autoflush=False,   # Don't auto-flush (we control when to flush)
    bind=engine        # Bind to our engine
)


# ============================================================
# CONCEPT 3: Create Declarative Base
# ============================================================
# Base class for all our ORM models
# Models inherit from this to become database tables

Base = declarative_base()


# ============================================================
# CONCEPT 4: Database Session Dependency
# ============================================================
# This is a FastAPI dependency that:
# 1. Creates a new session for each request
# 2. Yields the session to the endpoint
# 3. Closes the session after the request (cleanup)

def get_db():
    """
    Database session dependency
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    The session is automatically closed after the request,
    even if an error occurs (thanks to try/finally).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
