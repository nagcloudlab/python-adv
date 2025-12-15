"""
Test Configuration and Fixtures
================================
Shared fixtures for all tests.

pytest automatically discovers conftest.py and makes
fixtures available to all tests in the same directory.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import db, Database


# ============================================================
# FIXTURE 1: TestClient
# ============================================================

@pytest.fixture
def client():
    """
    Create a TestClient for the FastAPI app
    
    TestClient allows us to make HTTP requests to our app
    without running a server.
    
    Usage:
        def test_something(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    return TestClient(app)


# ============================================================
# FIXTURE 2: Reset Database
# ============================================================

@pytest.fixture(autouse=True)
def reset_database():
    """
    Reset database before each test
    
    autouse=True means this runs automatically for every test.
    This ensures each test starts with a clean database.
    """
    db.reset()
    yield  # Test runs here
    # Cleanup after test (if needed)


# ============================================================
# FIXTURE 3: Authenticated Client
# ============================================================

@pytest.fixture
def auth_client(client):
    """
    Client with authentication headers
    
    Usage:
        def test_protected(auth_client):
            response = auth_client.get("/protected")
    """
    client.headers["X-API-Key"] = "admin-key-123"
    return client


@pytest.fixture
def user_client(client):
    """
    Client authenticated as regular user
    """
    client.headers["X-API-Key"] = "user1-key-456"
    return client


# ============================================================
# FIXTURE 4: Sample Data
# ============================================================

@pytest.fixture
def sample_task():
    """
    Sample task data for testing
    """
    return {
        "title": "Test Task",
        "description": "A task for testing",
        "priority": 3
    }


@pytest.fixture
def sample_tasks():
    """
    Multiple sample tasks
    """
    return [
        {"title": "Task 1", "priority": 1},
        {"title": "Task 2", "priority": 2},
        {"title": "Task 3", "priority": 3},
    ]


# ============================================================
# FIXTURE 5: Create Test Task
# ============================================================

@pytest.fixture
def created_task(auth_client, sample_task):
    """
    Create a task and return it
    
    Useful when tests need an existing task
    """
    response = auth_client.post("/tasks", json=sample_task)
    return response.json()


# ============================================================
# FIXTURE 6: Empty Database
# ============================================================

@pytest.fixture
def empty_db():
    """
    Completely empty database (no seed data)
    """
    db.clear()
    yield db
    db.reset()  # Restore after test
