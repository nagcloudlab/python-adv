"""
Level 2: Path Parameters
========================
Concepts Covered:
    - Dynamic URL paths with {parameter}
    - Type hints for automatic validation
    - Multiple path parameters
    - Enum for predefined values
    - Path ordering (fixed vs dynamic)

Run Command:
    uvicorn main:app --reload

Test URLs:
    http://127.0.0.1:8000/tasks/1
    http://127.0.0.1:8000/tasks/abc          → Type error (expects int)
    http://127.0.0.1:8000/users/john
    http://127.0.0.1:8000/users/john/tasks/5
    http://127.0.0.1:8000/tasks/status/pending
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from enum import Enum

app = FastAPI(
    title="Task Manager API - Level 2",
    description="Learning Path Parameters",
    version="2.0.0"
)

# ============================================================
# Sample Data (In-memory database simulation)
# ============================================================

tasks_db = {
    1: {"id": 1, "title": "Learn FastAPI", "status": "in_progress", "assignee": "john"},
    2: {"id": 2, "title": "Build REST API", "status": "pending", "assignee": "jane"},
    3: {"id": 3, "title": "Write Tests", "status": "completed", "assignee": "john"},
    4: {"id": 4, "title": "Deploy App", "status": "pending", "assignee": "jane"},
    5: {"id": 5, "title": "Documentation", "status": "in_progress", "assignee": "john"}
}

users_db = {
    "john": {"username": "john", "full_name": "John Doe", "role": "developer"},
    "jane": {"username": "jane", "full_name": "Jane Smith", "role": "manager"}
}


# ============================================================
# CONCEPT 1: Basic Path Parameter (Integer)
# ============================================================
# Syntax: {parameter_name} in the path
# Type hint (task_id: int) enables automatic validation

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    Get task by ID
    
    - task_id must be an integer (automatic validation)
    - Try: /tasks/1 (works) vs /tasks/abc (validation error)
    """
    if task_id in tasks_db:
        return tasks_db[task_id]
    return {"error": "Task not found", "task_id": task_id}


# ============================================================
# CONCEPT 2: String Path Parameter
# ============================================================
# String parameters accept any text value

@app.get("/users/{username}")
def get_user(username: str):
    """
    Get user by username
    
    - username is a string, accepts any value
    - Example: /users/john, /users/jane
    """
    if username in users_db:
        return users_db[username]
    return {"error": "User not found", "username": username}


# ============================================================
# CONCEPT 3: Multiple Path Parameters
# ============================================================
# Combine multiple dynamic segments in URL

@app.get("/users/{username}/tasks/{task_id}")
def get_user_task(username: str, task_id: int):
    """
    Get specific task for a user
    
    - Two path parameters: username (str) and task_id (int)
    - Example: /users/john/tasks/1
    """
    # Check user exists
    if username not in users_db:
        return {"error": "User not found", "username": username}
    
    # Check task exists and belongs to user
    if task_id in tasks_db:
        task = tasks_db[task_id]
        if task["assignee"] == username:
            return {
                "user": users_db[username],
                "task": task
            }
        return {"error": "Task not assigned to this user"}
    
    return {"error": "Task not found", "task_id": task_id}


# ============================================================
# CONCEPT 4: Enum for Predefined Values
# ============================================================
# Use Enum to restrict path parameter to specific values

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


@app.get("/tasks/status/{status}")
def get_tasks_by_status(status: TaskStatus):
    """
    Get tasks by status
    
    - status MUST be one of: pending, in_progress, completed
    - Invalid values return automatic validation error
    - Check /docs to see dropdown in Swagger UI
    """
    filtered_tasks = [
        task for task in tasks_db.values() 
        if task["status"] == status.value
    ]
    return {
        "status": status.value,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }


# ============================================================
# CONCEPT 5: Path Order Matters!
# ============================================================
# Fixed paths MUST be defined BEFORE dynamic paths
# Otherwise, the dynamic path will match first

# This MUST come BEFORE /tasks/{task_id}
# But since we already defined /tasks/{task_id} above,
# we use a different base path for demonstration

@app.get("/items/count")
def get_items_count():
    """
    Fixed path: /items/count
    
    This is defined BEFORE /items/{item_id}
    So /items/count won't be treated as item_id="count"
    """
    return {"total_items": 100}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """
    Dynamic path: /items/{item_id}
    
    If /items/count was defined AFTER this,
    it would never be reached (count would be treated as item_id)
    """
    return {"item_id": item_id, "name": f"Item {item_id}"}


# ============================================================
# CONCEPT 6: Path Parameter with File Path
# ============================================================
# Use :path converter for paths containing slashes

@app.get("/files/{file_path:path}")
def get_file(file_path: str):
    """
    Path parameter containing slashes
    
    - :path allows slashes in the parameter
    - Example: /files/documents/report.pdf
    - Without :path, slashes would break the URL
    """
    return {
        "file_path": file_path,
        "message": f"Accessing file: {file_path}"
    }


# ============================================================
# ADDITIONAL EXAMPLES
# ============================================================

# Example: User role access
class UserRole(str, Enum):
    admin = "admin"
    developer = "developer"
    manager = "manager"
    viewer = "viewer"


@app.get("/roles/{role}/users")
def get_users_by_role(role: UserRole):
    """
    Get users by role (Enum parameter)
    
    - Only accepts: admin, developer, manager, viewer
    """
    users = [
        user for user in users_db.values()
        if user["role"] == role.value
    ]
    return {"role": role.value, "users": users}


# Example: Combining path and returning different data
@app.get("/summary/{entity}/{entity_id}")
def get_summary(entity: str, entity_id: int):
    """
    Generic summary endpoint
    
    - entity: 'task' or 'user' (as string for flexibility)
    - entity_id: numeric ID
    - Example: /summary/task/1
    """
    if entity == "task":
        if entity_id in tasks_db:
            return {"entity": "task", "data": tasks_db[entity_id]}
    elif entity == "user":
        # For users, we'd need different lookup
        return {"entity": "user", "message": "User lookup by ID not implemented"}
    
    return {"error": f"Unknown entity: {entity}"}


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
def root():
    """API Root - Shows available endpoints"""
    return {
        "message": "Level 2 - Path Parameters",
        "endpoints": [
            "GET /tasks/{task_id}",
            "GET /users/{username}",
            "GET /users/{username}/tasks/{task_id}",
            "GET /tasks/status/{status}",
            "GET /items/count",
            "GET /items/{item_id}",
            "GET /files/{file_path:path}",
            "GET /roles/{role}/users"
        ]
    }
