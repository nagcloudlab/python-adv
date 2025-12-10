"""
Level 14: APIRouter & Project Structure
========================================
This is the main entry point of the application.

Project Structure:
    level_14_routers_structure/
    ├── main.py                 # This file - app entry point
    ├── app/
    │   ├── __init__.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py       # Settings & configuration
    │   │   └── dependencies.py # Shared dependencies
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   ├── tasks.py        # Task endpoints
    │   │   ├── users.py        # User endpoints
    │   │   └── admin.py        # Admin endpoints
    │   ├── models/
    │   │   ├── __init__.py
    │   │   └── database.py     # Simulated database
    │   └── schemas/
    │       ├── __init__.py
    │       ├── task.py         # Task Pydantic models
    │       └── user.py         # User Pydantic models
    └── requirements.txt

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from app.routers import tasks, users, admin
from app.core.config import settings

# Create FastAPI app with settings
app = FastAPI(
    title=settings.APP_NAME,
    description="Learning APIRouter & Project Structure",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================
# Include Routers
# ============================================================
# Each router handles a group of related endpoints

# Tasks router - /tasks/*
app.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)

# Users router - /users/*
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Admin router - /admin/*
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)


# ============================================================
# Root Endpoints (in main.py)
# ============================================================

@app.get("/", tags=["Root"])
def root():
    """API Root"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "tasks": "/tasks",
            "users": "/users",
            "admin": "/admin"
        }
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "debug": settings.DEBUG
    }


@app.get("/info", tags=["Root"])
def api_info():
    """API Information"""
    return {
        "message": "Level 14 - APIRouter & Project Structure",
        "concepts": [
            "APIRouter for grouping endpoints",
            "Project structure with multiple files",
            "Routers with prefix and tags",
            "Shared dependencies across modules",
            "Centralized configuration",
            "Pydantic schemas in separate files"
        ],
        "structure": {
            "main.py": "Application entry point",
            "app/core/config.py": "Settings & configuration",
            "app/core/dependencies.py": "Shared dependencies",
            "app/routers/": "Endpoint routers",
            "app/models/": "Database models",
            "app/schemas/": "Pydantic schemas"
        }
    }
