"""
Level 15: Database Integration (SQLAlchemy)
============================================
Learn to connect FastAPI to a real database using SQLAlchemy ORM.

This level uses SQLite for simplicity - no database server needed!
The database file (tasks.db) will be created automatically.

Concepts Covered:
    - SQLAlchemy setup with FastAPI
    - Database models (ORM)
    - Database session management
    - CRUD operations with database
    - Relationships (one-to-many)
    - Database migrations basics

Project Structure:
    level_15_database/
    ├── main.py                 # This file
    ├── app/
    │   ├── core/
    │   │   ├── config.py       # Settings
    │   │   └── database.py     # Database connection
    │   ├── models/
    │   │   └── models.py       # SQLAlchemy models
    │   ├── schemas/
    │   │   ├── task.py         # Task schemas
    │   │   └── user.py         # User schemas
    │   └── routers/
    │       ├── tasks.py        # Task endpoints
    │       └── users.py        # User endpoints
    └── tasks.db                # SQLite database (auto-created)

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from app.core.database import engine, Base
from app.routers import tasks, users

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Task Manager API - Level 15",
    description="Database Integration with SQLAlchemy",
    version="15.0.0"
)

# Include routers
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(users.router, prefix="/users", tags=["Users"])


@app.get("/", tags=["Root"])
def root():
    """API Root"""
    return {
        "message": "Level 15 - Database Integration (SQLAlchemy)",
        "database": "SQLite (tasks.db)",
        "concepts": [
            "SQLAlchemy ORM",
            "Database sessions",
            "CRUD operations",
            "Model relationships",
            "Dependency injection for DB"
        ],
        "endpoints": {
            "users": "/users",
            "tasks": "/tasks"
        },
        "test_flow": [
            "1. POST /users - Create a user first",
            "2. POST /tasks - Create tasks for user",
            "3. GET /users/{id}/tasks - See user's tasks"
        ]
    }


@app.get("/health", tags=["Root"])
def health():
    """Health check"""
    return {"status": "healthy", "database": "connected"}
