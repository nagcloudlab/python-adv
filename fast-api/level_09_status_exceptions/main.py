"""
Level 9: Status Codes & Exception Handling
==========================================
Concepts Covered:
    - HTTP status codes overview
    - Setting status codes on responses
    - HTTPException for error responses
    - Custom exception classes
    - Exception handlers (@app.exception_handler)
    - RequestValidationError handling
    - Generic exception handling
    - Error response models

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs (Swagger UI)
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

app = FastAPI(
    title="Task Manager API - Level 9",
    description="Learning Status Codes & Exception Handling",
    version="9.0.0"
)


# ============================================================
# Sample Data
# ============================================================

tasks_db = {
    1: {"id": 1, "title": "Learn FastAPI", "status": "completed"},
    2: {"id": 2, "title": "Build API", "status": "in_progress"},
    3: {"id": 3, "title": "Write Tests", "status": "pending"},
}

users_db = {
    "admin": {"username": "admin", "role": "admin", "active": True},
    "user1": {"username": "user1", "role": "user", "active": True},
    "banned": {"username": "banned", "role": "user", "active": False},
}


# ============================================================
# CONCEPT 1: Explicit Status Codes
# ============================================================
# Use status_code parameter to set response status

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None


# 201 Created - Resource created successfully
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """
    Create task - Returns 201 Created
    
    201 is the proper status for resource creation
    """
    new_id = max(tasks_db.keys()) + 1
    new_task = {"id": new_id, "title": task.title, "status": "pending"}
    tasks_db[new_id] = new_task
    return new_task


# 204 No Content - Success but no content to return
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """
    Delete task - Returns 204 No Content
    
    204 means success but no response body
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]
    # No return = empty response with 204


# 200 OK (default)
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    Get task - Returns 200 OK (default)
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]


# ============================================================
# CONCEPT 2: HTTPException - Basic Usage
# ============================================================

@app.get("/tasks/{task_id}/basic")
def get_task_basic_exception(task_id: int):
    """
    HTTPException with status code and detail message
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    return tasks_db[task_id]


# ============================================================
# CONCEPT 3: HTTPException with Headers
# ============================================================

@app.get("/tasks/{task_id}/with-headers")
def get_task_with_headers(task_id: int):
    """
    HTTPException with custom headers
    
    Useful for auth errors (WWW-Authenticate header)
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
            headers={"X-Error-Code": "TASK_NOT_FOUND"}
        )
    return tasks_db[task_id]


# ============================================================
# CONCEPT 4: HTTPException with Dict Detail
# ============================================================

@app.get("/tasks/{task_id}/detailed")
def get_task_detailed_error(task_id: int):
    """
    HTTPException with detailed error object
    
    detail can be a dict for richer error info
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "TASK_NOT_FOUND",
                "message": f"Task with id {task_id} does not exist",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    return tasks_db[task_id]


# ============================================================
# CONCEPT 5: Different Status Codes for Different Errors
# ============================================================

@app.get("/users/{username}/tasks")
def get_user_tasks(username: str):
    """
    Multiple error types with appropriate status codes
    
    - 404: User not found
    - 403: User is banned/inactive
    """
    user = users_db.get(username)
    
    # 404 Not Found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    # 403 Forbidden
    if not user["active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User '{username}' is inactive/banned"
        )
    
    # Return user's tasks
    user_tasks = [t for t in tasks_db.values()]
    return {"user": username, "tasks": user_tasks}


# ============================================================
# CONCEPT 6: Custom Exception Classes
# ============================================================

class TaskNotFoundException(Exception):
    """Custom exception for task not found"""
    def __init__(self, task_id: int):
        self.task_id = task_id
        self.message = f"Task with id {task_id} not found"
        super().__init__(self.message)


class InsufficientPermissionException(Exception):
    """Custom exception for permission errors"""
    def __init__(self, username: str, action: str):
        self.username = username
        self.action = action
        self.message = f"User '{username}' cannot perform action: {action}"
        super().__init__(self.message)


class RateLimitExceededException(Exception):
    """Custom exception for rate limiting"""
    def __init__(self, limit: int, reset_time: datetime):
        self.limit = limit
        self.reset_time = reset_time
        super().__init__(f"Rate limit of {limit} exceeded")


# ============================================================
# CONCEPT 7: Exception Handlers
# ============================================================

@app.exception_handler(TaskNotFoundException)
async def task_not_found_handler(request: Request, exc: TaskNotFoundException):
    """
    Handle TaskNotFoundException globally
    
    Any endpoint raising TaskNotFoundException will return this response
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "TASK_NOT_FOUND",
            "message": exc.message,
            "task_id": exc.task_id,
            "path": str(request.url)
        }
    )


@app.exception_handler(InsufficientPermissionException)
async def permission_error_handler(request: Request, exc: InsufficientPermissionException):
    """Handle permission errors"""
    return JSONResponse(
        status_code=403,
        content={
            "error": "PERMISSION_DENIED",
            "message": exc.message,
            "username": exc.username,
            "action": exc.action
        }
    )


@app.exception_handler(RateLimitExceededException)
async def rate_limit_handler(request: Request, exc: RateLimitExceededException):
    """Handle rate limit errors with Retry-After header"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "RATE_LIMIT_EXCEEDED",
            "message": f"Rate limit of {exc.limit} requests exceeded",
            "retry_after": exc.reset_time.isoformat()
        },
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": str(exc.limit),
            "X-RateLimit-Reset": exc.reset_time.isoformat()
        }
    )


# Endpoints using custom exceptions
@app.get("/v2/tasks/{task_id}")
def get_task_v2(task_id: int):
    """
    Get task using custom exception
    
    Raises TaskNotFoundException → handled by exception handler
    """
    if task_id not in tasks_db:
        raise TaskNotFoundException(task_id)
    return tasks_db[task_id]


@app.delete("/v2/tasks/{task_id}")
def delete_task_v2(task_id: int, username: str = "user1"):
    """
    Delete task with permission check
    
    Only admins can delete tasks
    """
    if task_id not in tasks_db:
        raise TaskNotFoundException(task_id)
    
    user = users_db.get(username)
    if not user or user["role"] != "admin":
        raise InsufficientPermissionException(username, "delete_task")
    
    del tasks_db[task_id]
    return {"message": "Task deleted"}


@app.get("/v2/limited")
def rate_limited_endpoint():
    """
    Simulated rate-limited endpoint
    
    Always raises RateLimitExceededException for demo
    """
    raise RateLimitExceededException(
        limit=100,
        reset_time=datetime.now()
    )


# ============================================================
# CONCEPT 8: Handle Validation Errors
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors
    
    Transforms default 422 error into custom format
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": errors,
            "body": exc.body
        }
    )


# Endpoint to test validation error handler
class StrictTask(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    priority: int = Field(..., ge=1, le=5)
    tags: List[str] = Field(..., min_length=1)


@app.post("/tasks/strict")
def create_strict_task(task: StrictTask):
    """
    Create task with strict validation
    
    Send invalid data to see custom validation error response
    """
    return {"message": "Task created", "task": task.model_dump()}


# ============================================================
# CONCEPT 9: Generic Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unhandled exceptions
    
    Prevents exposing internal errors to clients
    In production: log the error, return generic message
    """
    # In production, log the error:
    # logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "request_id": "req-12345",  # Would be generated
            # Don't expose exc details in production!
            "debug_info": str(exc)  # Remove in production
        }
    )


@app.get("/error/unexpected")
def trigger_unexpected_error():
    """
    Endpoint that raises unexpected error
    
    Demonstrates generic exception handler
    """
    # Simulate unexpected error
    result = 1 / 0  # ZeroDivisionError
    return {"result": result}


# ============================================================
# CONCEPT 10: Status Codes Reference Endpoints
# ============================================================

# 200 OK
@app.get("/status/200")
def status_200():
    """200 OK - Standard success response"""
    return {"status": 200, "message": "OK"}


# 201 Created
@app.post("/status/201", status_code=status.HTTP_201_CREATED)
def status_201():
    """201 Created - Resource created"""
    return {"status": 201, "message": "Created"}


# 202 Accepted
@app.post("/status/202", status_code=status.HTTP_202_ACCEPTED)
def status_202():
    """202 Accepted - Request accepted for processing"""
    return {"status": 202, "message": "Accepted", "job_id": "job-12345"}


# 204 No Content
@app.delete("/status/204", status_code=status.HTTP_204_NO_CONTENT)
def status_204():
    """204 No Content - Success with no body"""
    pass


# 400 Bad Request
@app.get("/status/400")
def status_400():
    """400 Bad Request - Invalid request"""
    raise HTTPException(status_code=400, detail="Bad request - invalid parameters")


# 401 Unauthorized
@app.get("/status/401")
def status_401():
    """401 Unauthorized - Authentication required"""
    raise HTTPException(
        status_code=401,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )


# 403 Forbidden
@app.get("/status/403")
def status_403():
    """403 Forbidden - Authenticated but not authorized"""
    raise HTTPException(status_code=403, detail="You don't have permission")


# 404 Not Found
@app.get("/status/404")
def status_404():
    """404 Not Found - Resource doesn't exist"""
    raise HTTPException(status_code=404, detail="Resource not found")


# 409 Conflict
@app.post("/status/409")
def status_409():
    """409 Conflict - Resource already exists"""
    raise HTTPException(status_code=409, detail="Resource already exists")


# 422 Unprocessable Entity
@app.post("/status/422")
def status_422():
    """422 Unprocessable Entity - Validation error"""
    raise HTTPException(status_code=422, detail="Validation failed")


# 429 Too Many Requests
@app.get("/status/429")
def status_429():
    """429 Too Many Requests - Rate limited"""
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded",
        headers={"Retry-After": "60"}
    )


# 500 Internal Server Error
@app.get("/status/500")
def status_500():
    """500 Internal Server Error - Server error"""
    raise HTTPException(status_code=500, detail="Internal server error")


# 503 Service Unavailable
@app.get("/status/503")
def status_503():
    """503 Service Unavailable - Service down"""
    raise HTTPException(
        status_code=503,
        detail="Service temporarily unavailable",
        headers={"Retry-After": "300"}
    )


# ============================================================
# CONCEPT 11: Error Response Models (for documentation)
# ============================================================

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    details: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TaskResponse(BaseModel):
    id: int
    title: str
    status: str


@app.get(
    "/documented/tasks/{task_id}",
    response_model=TaskResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
def get_task_documented(task_id: int):
    """
    Get task with documented error responses
    
    Swagger UI shows possible error responses
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "TASK_NOT_FOUND",
                "message": f"Task {task_id} not found",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    return tasks_db[task_id]


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 9 - Status Codes & Exception Handling",
        "concepts": [
            "status_code parameter",
            "HTTPException",
            "Custom exceptions",
            "@app.exception_handler",
            "RequestValidationError handling",
            "Generic exception handler"
        ],
        "test_endpoints": {
            "basic": [
                "POST /tasks (201 Created)",
                "DELETE /tasks/{id} (204 No Content)",
                "GET /tasks/{id} (200 OK / 404)"
            ],
            "http_exception": [
                "GET /tasks/{id}/basic",
                "GET /tasks/{id}/with-headers",
                "GET /tasks/{id}/detailed"
            ],
            "custom_exceptions": [
                "GET /v2/tasks/{id}",
                "DELETE /v2/tasks/{id}?username=user1",
                "GET /v2/limited"
            ],
            "validation": [
                "POST /tasks/strict (send invalid data)"
            ],
            "status_reference": [
                "/status/200 through /status/503"
            ]
        }
    }
