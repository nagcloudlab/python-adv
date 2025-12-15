"""
Simulated Database
==================
In a real application, this would be SQLAlchemy models
or other database connection.
"""

from datetime import datetime

# Simulated Tasks Database
tasks_db = {
    1: {
        "id": 1,
        "title": "Learn FastAPI",
        "description": "Complete FastAPI tutorial",
        "status": "completed",
        "priority": 5,
        "owner_id": "user1",
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-02T15:30:00"
    },
    2: {
        "id": 2,
        "title": "Build REST API",
        "description": "Create a production API",
        "status": "in_progress",
        "priority": 4,
        "owner_id": "user1",
        "created_at": "2024-01-03T09:00:00",
        "updated_at": "2024-01-03T09:00:00"
    },
    3: {
        "id": 3,
        "title": "Write Tests",
        "description": "Add unit and integration tests",
        "status": "pending",
        "priority": 3,
        "owner_id": "admin",
        "created_at": "2024-01-04T11:00:00",
        "updated_at": "2024-01-04T11:00:00"
    }
}

# Simulated Users Database
users_db = {
    "admin": {
        "id": "admin",
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00"
    },
    "user1": {
        "id": "user1",
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "role": "user",
        "is_active": True,
        "created_at": "2024-01-02T00:00:00"
    },
    "user2": {
        "id": "user2",
        "username": "jane_doe",
        "email": "jane@example.com",
        "full_name": "Jane Doe",
        "role": "user",
        "is_active": False,  # Inactive user
        "created_at": "2024-01-03T00:00:00"
    }
}


def get_next_task_id() -> int:
    """Get next available task ID"""
    if not tasks_db:
        return 1
    return max(tasks_db.keys()) + 1
