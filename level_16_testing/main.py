"""
Level 16: Testing FastAPI Applications
=======================================
Learn to test FastAPI applications using pytest and TestClient.

Concepts Covered:
    - pytest basics
    - TestClient for API testing
    - Testing endpoints (GET, POST, PUT, DELETE)
    - Testing with authentication
    - Database testing with fixtures
    - Mocking dependencies
    - Test organization

Project Structure:
    level_16_testing/
    ├── main.py                 # This file - app entry point
    ├── app/
    │   ├── __init__.py
    │   ├── database.py         # In-memory database
    │   ├── schemas.py          # Pydantic models
    │   ├── dependencies.py     # Dependencies
    │   └── routers/
    │       └── tasks.py        # Task endpoints
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py         # Shared fixtures
    │   ├── test_main.py        # Root endpoint tests
    │   ├── test_tasks.py       # Task endpoint tests
    │   └── test_auth.py        # Auth tests
    └── requirements.txt

Run Tests:
    pytest                      # Run all tests
    pytest -v                   # Verbose output
    pytest tests/test_tasks.py  # Run specific file
    pytest -k "test_create"     # Run tests matching pattern

Run App:
    uvicorn main:app --reload
"""

from fastapi import FastAPI
from app.routers import tasks

app = FastAPI(
    title="Task Manager API - Level 16",
    description="Learning Testing with pytest",
    version="16.0.0"
)

# Include routers
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])


@app.get("/", tags=["Root"])
def root():
    """Root endpoint"""
    return {
        "message": "Level 16 - Testing FastAPI",
        "status": "running"
    }


@app.get("/health", tags=["Root"])
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/info", tags=["Root"])
def info():
    """API Information"""
    return {
        "message": "Level 16 - Testing",
        "concepts": [
            "pytest basics",
            "TestClient",
            "Testing CRUD endpoints",
            "Test fixtures",
            "Mocking dependencies",
            "Database testing"
        ],
        "run_tests": "pytest -v"
    }
