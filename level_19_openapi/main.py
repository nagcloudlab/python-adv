"""
Level 19: OpenAPI Customization
================================
Learn to customize API documentation and OpenAPI schema.

Concepts Covered:
    - FastAPI app metadata
    - Tags and tag metadata
    - Operation descriptions
    - Request/Response examples
    - Deprecating endpoints
    - Custom OpenAPI schema
    - Hiding endpoints from docs
    - Multiple response types
    - External documentation links

Run Command:
    uvicorn main:app --reload

Documentation:
    - Swagger UI: http://127.0.0.1:8000/docs
    - ReDoc: http://127.0.0.1:8000/redoc
    - OpenAPI JSON: http://127.0.0.1:8000/openapi.json
"""

from fastapi import FastAPI, Query, Path, Body, HTTPException, status
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ============================================================
# CONCEPT 1: App Metadata
# ============================================================

app = FastAPI(
    # Basic info
    title="Task Manager API",
    description="""
## Task Manager API 🚀

A comprehensive API for managing tasks and projects.

### Features

* **Tasks** - Create, read, update, delete tasks
* **Users** - User management and authentication
* **Projects** - Organize tasks into projects

### Authentication

This API uses API Key authentication. Include your API key in the `X-API-Key` header.

### Rate Limiting

* Free tier: 100 requests/hour
* Pro tier: 10,000 requests/hour

### Support

For support, contact [support@example.com](mailto:support@example.com)
    """,
    version="19.0.0",
    
    # Terms and contact
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "https://example.com/support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    
    # Documentation URLs
    docs_url="/docs",           # Swagger UI (default: /docs)
    redoc_url="/redoc",         # ReDoc (default: /redoc)
    openapi_url="/openapi.json", # OpenAPI schema (default: /openapi.json)
    
    # Servers (for OpenAPI spec)
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.example.com", "description": "Production server"},
        {"url": "https://staging-api.example.com", "description": "Staging server"},
    ]
)


# ============================================================
# CONCEPT 2: Tags with Metadata
# ============================================================

tags_metadata = [
    {
        "name": "Tasks",
        "description": "Operations for managing **tasks**. Create, read, update, and delete tasks.",
        "externalDocs": {
            "description": "Tasks documentation",
            "url": "https://example.com/docs/tasks"
        }
    },
    {
        "name": "Users",
        "description": "Operations for **user management**. Registration, authentication, and profiles.",
    },
    {
        "name": "Projects",
        "description": "Operations for managing **projects**. Organize tasks into projects.",
    },
    {
        "name": "Admin",
        "description": "**Administrative** operations. Requires admin privileges.",
    },
    {
        "name": "Health",
        "description": "Health check and status endpoints.",
    },
]

# Update app with tags metadata
app.openapi_tags = tags_metadata


# ============================================================
# CONCEPT 3: Pydantic Models with Examples
# ============================================================

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskBase(BaseModel):
    """Base task model with common fields"""
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="The title of the task",
        json_schema_extra={"example": "Complete API documentation"}
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Detailed description of the task",
        json_schema_extra={"example": "Write comprehensive documentation for all API endpoints"}
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Priority level (1=lowest, 5=highest)",
        json_schema_extra={"example": 3}
    )


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Review pull request",
                    "description": "Review the authentication PR from John",
                    "priority": 4
                },
                {
                    "title": "Fix login bug",
                    "description": "Users can't login with special characters in password",
                    "priority": 5
                }
            ]
        }
    }


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "completed",
                "priority": 5
            }
        }
    }


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int = Field(..., description="Unique task identifier", json_schema_extra={"example": 42})
    status: TaskStatus = Field(..., description="Current task status")
    owner_id: int = Field(..., description="ID of the task owner")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 42,
                "title": "Complete API documentation",
                "description": "Write comprehensive docs",
                "priority": 3,
                "status": "in_progress",
                "owner_id": 1,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-16T14:22:00Z"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "TASK_NOT_FOUND",
                "message": "Task with ID 42 was not found",
                "details": {"task_id": 42}
            }
        }
    }


# ============================================================
# Sample Data
# ============================================================

tasks_db = {
    1: {
        "id": 1,
        "title": "Learn FastAPI",
        "description": "Complete the FastAPI tutorial",
        "priority": 5,
        "status": "completed",
        "owner_id": 1,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-05T15:30:00Z"
    },
    2: {
        "id": 2,
        "title": "Build REST API",
        "description": "Create production-ready API",
        "priority": 4,
        "status": "in_progress",
        "owner_id": 1,
        "created_at": "2024-01-10T09:00:00Z",
        "updated_at": None
    }
}


# ============================================================
# CONCEPT 4: Endpoints with Rich Documentation
# ============================================================

@app.get(
    "/tasks",
    response_model=List[TaskResponse],
    tags=["Tasks"],
    summary="List all tasks",
    description="""
Retrieve a list of all tasks with optional filtering.

### Filtering Options

- **status**: Filter by task status
- **priority**: Filter by priority level
- **limit**: Maximum number of results (default: 100)
- **offset**: Number of results to skip (for pagination)

### Response

Returns a list of tasks matching the filter criteria.
    """,
    response_description="List of tasks",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Example Task",
                            "description": "Task description",
                            "priority": 3,
                            "status": "pending",
                            "owner_id": 1,
                            "created_at": "2024-01-15T10:00:00Z",
                            "updated_at": None
                        }
                    ]
                }
            }
        }
    }
)
def list_tasks(
    status: Optional[TaskStatus] = Query(
        default=None,
        description="Filter by status",
        example="pending"
    ),
    priority: Optional[int] = Query(
        default=None,
        ge=1,
        le=5,
        description="Filter by priority level"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum results to return"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of results to skip"
    )
):
    """
    List all tasks with optional filtering.
    
    This endpoint returns all tasks visible to the current user,
    with optional filtering by status and priority.
    """
    tasks = list(tasks_db.values())
    
    if status:
        tasks = [t for t in tasks if t["status"] == status.value]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]
    
    return tasks[offset:offset + limit]


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["Tasks"],
    summary="Get task by ID",
    description="Retrieve a specific task by its unique identifier.",
    responses={
        200: {"description": "Task found", "model": TaskResponse},
        404: {
            "description": "Task not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "TASK_NOT_FOUND",
                        "message": "Task with ID 999 was not found",
                        "details": {"task_id": 999}
                    }
                }
            }
        }
    }
)
def get_task(
    task_id: int = Path(
        ...,
        ge=1,
        description="The unique identifier of the task",
        example=42
    )
):
    """Get a specific task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "TASK_NOT_FOUND",
                "message": f"Task with ID {task_id} was not found",
                "details": {"task_id": task_id}
            }
        )
    return tasks_db[task_id]


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    summary="Create a new task",
    description="""
Create a new task with the provided data.

### Required Fields

- **title**: Task title (3-100 characters)

### Optional Fields

- **description**: Detailed description (max 500 characters)
- **priority**: Priority level 1-5 (default: 1)

### Returns

The created task with assigned ID and timestamps.
    """,
    responses={
        201: {"description": "Task created successfully", "model": TaskResponse},
        422: {"description": "Validation error"}
    }
)
def create_task(
    task: TaskCreate = Body(
        ...,
        openapi_examples={
            "simple": {
                "summary": "Simple task",
                "description": "A basic task with just a title",
                "value": {
                    "title": "Buy groceries"
                }
            },
            "detailed": {
                "summary": "Detailed task",
                "description": "A task with all fields filled",
                "value": {
                    "title": "Complete project proposal",
                    "description": "Write the Q2 project proposal including budget estimates",
                    "priority": 5
                }
            },
            "bug_fix": {
                "summary": "Bug fix task",
                "description": "Example of a bug fix task",
                "value": {
                    "title": "Fix authentication bug",
                    "description": "Users are logged out after 5 minutes",
                    "priority": 4
                }
            }
        }
    )
):
    """Create a new task."""
    task_id = max(tasks_db.keys()) + 1 if tasks_db else 1
    
    new_task = {
        "id": task_id,
        **task.model_dump(),
        "status": "pending",
        "owner_id": 1,
        "created_at": datetime.now().isoformat() + "Z",
        "updated_at": None
    }
    
    tasks_db[task_id] = new_task
    return new_task


@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["Tasks"],
    summary="Update a task",
    description="Update an existing task. Only provided fields will be updated.",
    responses={
        200: {"description": "Task updated successfully"},
        404: {"description": "Task not found", "model": ErrorResponse}
    }
)
def update_task(
    task_id: int = Path(..., ge=1, example=1),
    task_update: TaskUpdate = Body(...)
):
    """Update an existing task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            if field == "status":
                task[field] = value.value
            else:
                task[field] = value
    
    task["updated_at"] = datetime.now().isoformat() + "Z"
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
    summary="Delete a task",
    description="Permanently delete a task. This action cannot be undone.",
    responses={
        204: {"description": "Task deleted successfully"},
        404: {"description": "Task not found"}
    }
)
def delete_task(task_id: int = Path(..., ge=1)):
    """Delete a task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]


# ============================================================
# CONCEPT 5: Deprecated Endpoints
# ============================================================

@app.get(
    "/tasks/all",
    response_model=List[TaskResponse],
    tags=["Tasks"],
    summary="[DEPRECATED] Get all tasks",
    description="**Deprecated**: Use `GET /tasks` instead. This endpoint will be removed in v20.",
    deprecated=True,
    responses={
        200: {"description": "List of all tasks"}
    }
)
def get_all_tasks_deprecated():
    """
    **DEPRECATED**: Use GET /tasks instead.
    
    This endpoint is kept for backward compatibility and will be removed in version 20.
    """
    return list(tasks_db.values())


# ============================================================
# CONCEPT 6: Hidden Endpoints (not in docs)
# ============================================================

@app.get(
    "/internal/debug",
    include_in_schema=False  # Hide from OpenAPI docs
)
def debug_endpoint():
    """
    Internal debug endpoint.
    
    This endpoint is hidden from API documentation.
    """
    return {
        "debug": True,
        "tasks_count": len(tasks_db),
        "memory": "OK"
    }


# ============================================================
# CONCEPT 7: Multiple Response Types
# ============================================================

@app.get(
    "/tasks/{task_id}/export",
    tags=["Tasks"],
    summary="Export task",
    description="Export a task in different formats.",
    responses={
        200: {
            "description": "Task data",
            "content": {
                "application/json": {
                    "example": {"id": 1, "title": "Task"}
                },
                "text/csv": {
                    "example": "id,title,status\n1,Task,pending"
                },
                "text/plain": {
                    "example": "Task: Task (ID: 1, Status: pending)"
                }
            }
        },
        404: {"description": "Task not found"}
    }
)
def export_task(
    task_id: int = Path(..., ge=1),
    format: str = Query(default="json", enum=["json", "csv", "text"])
):
    """Export task in specified format."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if format == "csv":
        return f"id,title,status\n{task['id']},{task['title']},{task['status']}"
    elif format == "text":
        return f"Task: {task['title']} (ID: {task['id']}, Status: {task['status']})"
    else:
        return task


# ============================================================
# Health Endpoints
# ============================================================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running.",
    response_description="Health status"
)
def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get(
    "/",
    tags=["Health"],
    summary="API information",
    description="Get basic API information."
)
def root():
    """API root with information."""
    return {
        "message": "Level 19 - OpenAPI Customization",
        "version": "19.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }


# ============================================================
# CONCEPT 8: Custom OpenAPI Schema
# ============================================================

def custom_openapi():
    """
    Generate custom OpenAPI schema.
    
    This allows you to modify the generated schema,
    add custom fields, or change the structure.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers
    )
    
    # Add custom extension
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png",
        "altText": "Task Manager Logo"
    }
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authentication"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token authentication"
        }
    }
    
    # Apply security globally (optional)
    # openapi_schema["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override the default openapi() method
app.openapi = custom_openapi


# ============================================================
# Info endpoint
# ============================================================

@app.get("/info", tags=["Health"])
def info():
    """API Information"""
    return {
        "message": "Level 19 - OpenAPI Customization",
        "concepts": [
            "App metadata (title, description, version)",
            "Tags with descriptions",
            "Operation summaries and descriptions",
            "Request/Response examples",
            "Multiple OpenAPI examples",
            "Deprecated endpoints",
            "Hidden endpoints (include_in_schema=False)",
            "Multiple response types",
            "Custom OpenAPI schema"
        ],
        "documentation": {
            "swagger_ui": "http://localhost:8000/docs",
            "redoc": "http://localhost:8000/redoc",
            "openapi_json": "http://localhost:8000/openapi.json"
        }
    }
