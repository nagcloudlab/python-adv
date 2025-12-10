"""
Level 4: Request Body (Pydantic Models)
=======================================
Concepts Covered:
    - Pydantic BaseModel for request validation
    - POST, PUT, PATCH, DELETE methods
    - Required vs Optional fields
    - Nested models
    - Field defaults and examples
    - model_dump() for serialization
    - Combining body with path/query parameters

Run Command:
    uvicorn main:app --reload

Test:
    Use Swagger UI: http://127.0.0.1:8000/docs
    (Best way to test POST/PUT requests interactively)
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Task Manager API - Level 4",
    description="Learning Request Body with Pydantic",
    version="4.0.0"
)

# ============================================================
# In-Memory Database
# ============================================================

tasks_db = {}
task_id_counter = 1


# ============================================================
# CONCEPT 1: Basic Pydantic Model
# ============================================================
# BaseModel automatically validates incoming JSON data

class TaskCreate(BaseModel):
    """
    Pydantic model for creating a task
    
    - Required fields: title
    - Optional fields: description, priority
    - Default values provided for optional fields
    """
    title: str
    description: Optional[str] = None
    priority: int = 1


# Basic POST endpoint
@app.post("/tasks")
def create_task(task: TaskCreate):
    """
    Create a new task
    
    Request Body (JSON):
    {
        "title": "Learn Pydantic",
        "description": "Study Pydantic models",
        "priority": 2
    }
    
    - title: Required
    - description: Optional (defaults to null)
    - priority: Optional (defaults to 1)
    """
    global task_id_counter
    
    new_task = {
        "id": task_id_counter,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    tasks_db[task_id_counter] = new_task
    task_id_counter += 1
    
    return {"message": "Task created", "task": new_task}


# ============================================================
# CONCEPT 2: Enum in Pydantic Model
# ============================================================

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskWithStatus(BaseModel):
    """Model with Enum field"""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending


@app.post("/tasks/with-status")
def create_task_with_status(task: TaskWithStatus):
    """
    Create task with status enum
    
    status must be one of: pending, in_progress, completed
    Invalid values will return validation error
    """
    global task_id_counter
    
    new_task = {
        "id": task_id_counter,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "created_at": datetime.now().isoformat()
    }
    
    tasks_db[task_id_counter] = new_task
    task_id_counter += 1
    
    return {"message": "Task created", "task": new_task}


# ============================================================
# CONCEPT 3: Nested Models
# ============================================================

class Tag(BaseModel):
    """Nested model for tags"""
    name: str
    color: str = "blue"


class Assignee(BaseModel):
    """Nested model for assignee"""
    username: str
    email: str


class TaskWithNested(BaseModel):
    """Model with nested objects"""
    title: str
    description: Optional[str] = None
    tags: List[Tag] = []
    assignee: Optional[Assignee] = None


@app.post("/tasks/detailed")
def create_detailed_task(task: TaskWithNested):
    """
    Create task with nested objects
    
    Request Body Example:
    {
        "title": "Complex Task",
        "description": "Task with nested data",
        "tags": [
            {"name": "urgent", "color": "red"},
            {"name": "backend", "color": "green"}
        ],
        "assignee": {
            "username": "john",
            "email": "john@example.com"
        }
    }
    """
    global task_id_counter
    
    new_task = {
        "id": task_id_counter,
        "title": task.title,
        "description": task.description,
        "tags": [tag.model_dump() for tag in task.tags],
        "assignee": task.assignee.model_dump() if task.assignee else None,
        "created_at": datetime.now().isoformat()
    }
    
    tasks_db[task_id_counter] = new_task
    task_id_counter += 1
    
    return {"message": "Detailed task created", "task": new_task}


# ============================================================
# CONCEPT 4: PUT - Full Update
# ============================================================

class TaskUpdate(BaseModel):
    """Model for full task update (PUT)"""
    title: str
    description: Optional[str] = None
    priority: int = 1
    status: TaskStatus = TaskStatus.pending


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    """
    Full update - Replace entire task
    
    PUT replaces the entire resource
    All fields should be provided (or defaults will be used)
    """
    if task_id not in tasks_db:
        return {"error": "Task not found", "task_id": task_id}
    
    updated_task = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status.value,
        "updated_at": datetime.now().isoformat()
    }
    
    tasks_db[task_id] = updated_task
    return {"message": "Task updated", "task": updated_task}


# ============================================================
# CONCEPT 5: PATCH - Partial Update
# ============================================================

class TaskPartialUpdate(BaseModel):
    """
    Model for partial update (PATCH)
    All fields are optional
    """
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[TaskStatus] = None


@app.patch("/tasks/{task_id}")
def partial_update_task(task_id: int, task: TaskPartialUpdate):
    """
    Partial update - Update only provided fields
    
    PATCH updates only the fields that are sent
    Unspecified fields remain unchanged
    
    Example: {"status": "completed"} - only updates status
    """
    if task_id not in tasks_db:
        return {"error": "Task not found", "task_id": task_id}
    
    stored_task = tasks_db[task_id]
    
    # Only update provided fields (exclude_unset=True is key!)
    update_data = task.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "status" and value:
            stored_task[field] = value.value  # Convert enum to string
        else:
            stored_task[field] = value
    
    stored_task["updated_at"] = datetime.now().isoformat()
    
    return {"message": "Task partially updated", "task": stored_task}


# ============================================================
# CONCEPT 6: DELETE
# ============================================================

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """
    Delete a task
    
    DELETE typically doesn't have a request body
    Resource identified by path parameter
    """
    if task_id not in tasks_db:
        return {"error": "Task not found", "task_id": task_id}
    
    deleted_task = tasks_db.pop(task_id)
    return {"message": "Task deleted", "task": deleted_task}


# ============================================================
# CONCEPT 7: Body + Path + Query Parameters Combined
# ============================================================

class CommentCreate(BaseModel):
    """Model for adding comment"""
    text: str
    author: str


@app.post("/tasks/{task_id}/comments")
def add_comment(
    task_id: int,                    # Path parameter
    comment: CommentCreate,          # Request body
    notify: bool = False             # Query parameter
):
    """
    Add comment to task
    
    Combines:
    - Path parameter: task_id
    - Request body: comment object
    - Query parameter: notify flag
    
    URL: POST /tasks/1/comments?notify=true
    Body: {"text": "Great progress!", "author": "john"}
    """
    if task_id not in tasks_db:
        return {"error": "Task not found", "task_id": task_id}
    
    new_comment = {
        "text": comment.text,
        "author": comment.author,
        "created_at": datetime.now().isoformat()
    }
    
    # Add comments list if doesn't exist
    if "comments" not in tasks_db[task_id]:
        tasks_db[task_id]["comments"] = []
    
    tasks_db[task_id]["comments"].append(new_comment)
    
    return {
        "message": "Comment added",
        "task_id": task_id,
        "comment": new_comment,
        "notification_sent": notify
    }


# ============================================================
# CONCEPT 8: Model with Examples (for Swagger UI)
# ============================================================

class TaskWithExample(BaseModel):
    """Model with example for documentation"""
    title: str
    description: Optional[str] = None
    priority: int = 1
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Complete Project Report",
                    "description": "Finish the Q4 project report",
                    "priority": 2
                }
            ]
        }
    }


@app.post("/tasks/example")
def create_task_with_example(task: TaskWithExample):
    """
    Create task - Check Swagger UI for pre-filled example
    
    The model_config provides example values shown in /docs
    """
    return {"message": "Task created", "data": task.model_dump()}


# ============================================================
# CONCEPT 9: List of Models in Request Body
# ============================================================

@app.post("/tasks/bulk")
def create_bulk_tasks(tasks: List[TaskCreate]):
    """
    Create multiple tasks at once
    
    Request Body (JSON Array):
    [
        {"title": "Task 1", "priority": 1},
        {"title": "Task 2", "priority": 2},
        {"title": "Task 3"}
    ]
    """
    global task_id_counter
    
    created_tasks = []
    for task in tasks:
        new_task = {
            "id": task_id_counter,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        tasks_db[task_id_counter] = new_task
        created_tasks.append(new_task)
        task_id_counter += 1
    
    return {
        "message": f"Created {len(created_tasks)} tasks",
        "tasks": created_tasks
    }


# ============================================================
# READ Endpoints (for testing)
# ============================================================

@app.get("/tasks")
def list_tasks():
    """List all tasks"""
    return {"count": len(tasks_db), "tasks": list(tasks_db.values())}


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Get single task by ID"""
    if task_id in tasks_db:
        return tasks_db[task_id]
    return {"error": "Task not found"}


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 4 - Request Body (Pydantic)",
        "tip": "Use /docs (Swagger UI) to test POST/PUT/PATCH/DELETE",
        "endpoints": {
            "POST": [
                "/tasks - Basic create",
                "/tasks/with-status - With enum",
                "/tasks/detailed - With nested models",
                "/tasks/bulk - Bulk create",
                "/tasks/{id}/comments - Add comment"
            ],
            "PUT": ["/tasks/{id} - Full update"],
            "PATCH": ["/tasks/{id} - Partial update"],
            "DELETE": ["/tasks/{id} - Delete task"],
            "GET": ["/tasks - List all", "/tasks/{id} - Get one"]
        }
    }
