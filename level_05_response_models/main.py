"""
Level 5: Response Models
========================
Concepts Covered:
    - response_model parameter
    - Filtering sensitive data (passwords, etc.)
    - response_model_exclude_unset
    - response_model_exclude / response_model_include
    - Different input vs output models
    - List response models
    - Union types for multiple responses
    - Nested response models

Run Command:
    uvicorn main:app --reload

Key Benefit:
    Response models automatically filter output data,
    ensuring sensitive fields are never exposed!
"""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Task Manager API - Level 5",
    description="Learning Response Models",
    version="5.0.0"
)


# ============================================================
# Sample Data (Simulating Database)
# ============================================================

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# Simulated database with sensitive data
users_db = {
    1: {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "hashed_password": "$2b$12$KIXQKp5z1RtP...",  # Sensitive!
        "is_active": True,
        "role": "admin",
        "created_at": "2024-01-15T10:30:00"
    },
    2: {
        "id": 2,
        "username": "jane_smith",
        "email": "jane@example.com",
        "hashed_password": "$2b$12$AnotherHash...",  # Sensitive!
        "is_active": True,
        "role": "user",
        "created_at": "2024-02-20T14:45:00"
    }
}

tasks_db = {
    1: {"id": 1, "title": "Learn FastAPI", "description": "Complete tutorial", "status": "completed", "priority": 1, "user_id": 1, "created_at": "2024-01-20T09:00:00"},
    2: {"id": 2, "title": "Build API", "description": None, "status": "in_progress", "priority": 2, "user_id": 1, "created_at": "2024-01-21T10:00:00"},
    3: {"id": 3, "title": "Write Tests", "description": "Unit and integration tests", "status": "pending", "priority": 1, "user_id": 2, "created_at": "2024-01-22T11:00:00"},
}


# ============================================================
# CONCEPT 1: Input vs Output Models
# ============================================================
# Different models for creating vs returning data

# Input model (for creating user)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str  # Plain password (input)


# Output model (for returning user) - NO PASSWORD!
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    model_config = {"from_attributes": True}


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    """
    Create user - Returns UserResponse (no password!)
    
    Input: UserCreate (has password)
    Output: UserResponse (no password field)
    
    Even though we return the full dict with hashed_password,
    FastAPI filters it out based on response_model!
    """
    # Simulate creating user
    new_user = {
        "id": 3,
        "username": user.username,
        "email": user.email,
        "hashed_password": f"hashed_{user.password}",  # Would be hashed
        "is_active": True,
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
    
    # Return full dict - FastAPI filters based on response_model
    return new_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """
    Get user by ID - Password is automatically filtered out
    
    The database record has hashed_password, but response_model
    ensures it's never sent to the client.
    """
    if user_id not in users_db:
        return {"error": "User not found"}
    
    return users_db[user_id]  # Full dict returned, but filtered


# ============================================================
# CONCEPT 2: Detailed Response Model
# ============================================================

class UserDetailResponse(BaseModel):
    """Extended user response with more fields"""
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    created_at: str
    task_count: int  # Computed field


@app.get("/users/{user_id}/detail", response_model=UserDetailResponse)
def get_user_detail(user_id: int):
    """
    Get detailed user info with computed fields
    
    task_count is computed at runtime, not stored in DB
    """
    if user_id not in users_db:
        return {"error": "User not found"}
    
    user = users_db[user_id]
    task_count = len([t for t in tasks_db.values() if t["user_id"] == user_id])
    
    return {
        **user,
        "task_count": task_count
    }


# ============================================================
# CONCEPT 3: List Response Model
# ============================================================

@app.get("/users", response_model=List[UserResponse])
def list_users():
    """
    List all users - Each user filtered through UserResponse
    
    Returns list, each item filtered by response_model
    Passwords removed from ALL users automatically
    """
    return list(users_db.values())


# ============================================================
# CONCEPT 4: response_model_exclude_unset
# ============================================================

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: int
    created_at: str


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    response_model_exclude_unset=True
)
def get_task(task_id: int):
    """
    Get task - Excludes fields that weren't explicitly set
    
    If description is None, it won't appear in response at all
    (instead of showing "description": null)
    
    Compare:
    - With exclude_unset: {"id": 1, "title": "...", "status": "..."}
    - Without: {"id": 1, "title": "...", "description": null, "status": "..."}
    """
    if task_id not in tasks_db:
        return {"error": "Task not found"}
    
    return tasks_db[task_id]


# ============================================================
# CONCEPT 5: response_model_exclude
# ============================================================

@app.get(
    "/tasks/{task_id}/minimal",
    response_model=TaskResponse,
    response_model_exclude={"description", "created_at", "priority"}
)
def get_task_minimal(task_id: int):
    """
    Get minimal task info - Specific fields excluded
    
    Returns only: id, title, status
    Excludes: description, created_at, priority
    """
    if task_id not in tasks_db:
        return {"error": "Task not found"}
    
    return tasks_db[task_id]


# ============================================================
# CONCEPT 6: response_model_include
# ============================================================

@app.get(
    "/tasks/{task_id}/summary",
    response_model=TaskResponse,
    response_model_include={"id", "title", "status"}
)
def get_task_summary(task_id: int):
    """
    Get task summary - Only specific fields included
    
    Opposite of exclude - whitelist approach
    Only returns: id, title, status
    """
    if task_id not in tasks_db:
        return {"error": "Task not found"}
    
    return tasks_db[task_id]


# ============================================================
# CONCEPT 7: Union Types for Multiple Response Types
# ============================================================

class TaskNotFound(BaseModel):
    error: str
    task_id: int
    suggestion: str = "Check if task ID is correct"


@app.get(
    "/tasks/{task_id}/safe",
    response_model=Union[TaskResponse, TaskNotFound]
)
def get_task_safe(task_id: int):
    """
    Get task with typed error response
    
    Returns either:
    - TaskResponse (if found)
    - TaskNotFound (if not found)
    
    Both are valid response types according to Union
    """
    if task_id in tasks_db:
        return tasks_db[task_id]
    
    return TaskNotFound(
        error="Task not found",
        task_id=task_id
    )


# ============================================================
# CONCEPT 8: Wrapper Response Model
# ============================================================

class TaskListResponse(BaseModel):
    """Wrapped list with metadata"""
    success: bool
    total: int
    page: int
    per_page: int
    tasks: List[TaskResponse]


@app.get("/tasks", response_model=TaskListResponse)
def list_tasks(page: int = 1, per_page: int = 10):
    """
    List tasks with metadata wrapper
    
    Response includes pagination info alongside data
    Common pattern for production APIs
    """
    all_tasks = list(tasks_db.values())
    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_tasks[start:end]
    
    return {
        "success": True,
        "total": len(all_tasks),
        "page": page,
        "per_page": per_page,
        "tasks": paginated
    }


# ============================================================
# CONCEPT 9: Nested Response Models
# ============================================================

class TaskOwner(BaseModel):
    """Minimal user info for nesting"""
    id: int
    username: str


class TaskWithOwner(BaseModel):
    """Task with nested owner info"""
    id: int
    title: str
    status: str
    owner: TaskOwner


@app.get("/tasks/{task_id}/with-owner", response_model=TaskWithOwner)
def get_task_with_owner(task_id: int):
    """
    Get task with nested owner information
    
    Owner is embedded as nested object
    Only minimal owner info included (no password!)
    """
    if task_id not in tasks_db:
        return {"error": "Task not found"}
    
    task = tasks_db[task_id]
    owner = users_db.get(task["user_id"], {})
    
    return {
        "id": task["id"],
        "title": task["title"],
        "status": task["status"],
        "owner": {
            "id": owner.get("id"),
            "username": owner.get("username")
        }
    }


# ============================================================
# CONCEPT 10: Different Models for Same Entity
# ============================================================

# Minimal response
class TaskBrief(BaseModel):
    id: int
    title: str


# Standard response
class TaskStandard(BaseModel):
    id: int
    title: str
    status: str
    priority: int


# Full response
class TaskFull(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    user_id: int
    created_at: str


@app.get("/tasks/{task_id}/brief", response_model=TaskBrief)
def get_task_brief(task_id: int):
    """Minimal task info"""
    if task_id not in tasks_db:
        return {"error": "not found"}
    return tasks_db[task_id]


@app.get("/tasks/{task_id}/standard", response_model=TaskStandard)
def get_task_standard(task_id: int):
    """Standard task info"""
    if task_id not in tasks_db:
        return {"error": "not found"}
    return tasks_db[task_id]


@app.get("/tasks/{task_id}/full", response_model=TaskFull)
def get_task_full(task_id: int):
    """Full task info"""
    if task_id not in tasks_db:
        return {"error": "not found"}
    return tasks_db[task_id]


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 5 - Response Models",
        "key_concept": "response_model filters output data automatically",
        "endpoints": {
            "users": [
                "POST /users - Create (password filtered)",
                "GET /users - List all (passwords filtered)",
                "GET /users/{id} - Get one (password filtered)",
                "GET /users/{id}/detail - With task count"
            ],
            "tasks": [
                "GET /tasks - List with wrapper",
                "GET /tasks/{id} - exclude_unset demo",
                "GET /tasks/{id}/minimal - exclude fields",
                "GET /tasks/{id}/summary - include only",
                "GET /tasks/{id}/safe - Union response",
                "GET /tasks/{id}/with-owner - Nested model",
                "GET /tasks/{id}/brief|standard|full - Multiple models"
            ]
        }
    }
