"""
Level 10: Dependency Injection
==============================
Concepts Covered:
    - Basic dependencies with Depends()
    - Dependencies with parameters
    - Class-based dependencies
    - Nested/chained dependencies
    - Dependencies with yield (cleanup)
    - Global dependencies
    - Path operation dependencies
    - Common patterns: auth, database, pagination

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs (Swagger UI)
"""

from fastapi import FastAPI, Depends, HTTPException, Header, Query, status
from typing import Optional, Annotated, List
from pydantic import BaseModel
from datetime import datetime
import secrets

app = FastAPI(
    title="Task Manager API - Level 10",
    description="Learning Dependency Injection",
    version="10.0.0"
)


# ============================================================
# Sample Data
# ============================================================

tasks_db = {
    1: {"id": 1, "title": "Learn FastAPI", "status": "completed", "owner": "admin"},
    2: {"id": 2, "title": "Build API", "status": "in_progress", "owner": "admin"},
    3: {"id": 3, "title": "Write Tests", "status": "pending", "owner": "user1"},
}

users_db = {
    "admin": {"username": "admin", "role": "admin", "api_key": "admin-key-12345"},
    "user1": {"username": "user1", "role": "user", "api_key": "user1-key-67890"},
}

# Simulated database connection
class FakeDatabase:
    def __init__(self):
        self.connected = False
        self.connection_id = None
    
    def connect(self):
        self.connected = True
        self.connection_id = secrets.token_hex(4)
        print(f"[DB] Connected: {self.connection_id}")
        return self
    
    def disconnect(self):
        print(f"[DB] Disconnected: {self.connection_id}")
        self.connected = False
        self.connection_id = None


# ============================================================
# CONCEPT 1: Basic Dependency (Function)
# ============================================================
# A dependency is just a function that FastAPI calls before your endpoint

def get_query_params(
    skip: int = 0,
    limit: int = 10
):
    """
    Simple dependency for pagination params
    
    Can be reused across multiple endpoints
    """
    return {"skip": skip, "limit": limit}


@app.get("/tasks")
def list_tasks(params: dict = Depends(get_query_params)):
    """
    List tasks using pagination dependency
    
    params is injected by FastAPI via Depends()
    """
    all_tasks = list(tasks_db.values())
    start = params["skip"]
    end = start + params["limit"]
    
    return {
        "pagination": params,
        "total": len(all_tasks),
        "tasks": all_tasks[start:end]
    }


# ============================================================
# CONCEPT 2: Dependency with Validation
# ============================================================

def validate_task_id(task_id: int):
    """
    Dependency that validates and returns task
    
    Raises 404 if task not found
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    return tasks_db[task_id]


@app.get("/tasks/{task_id}")
def get_task(task: dict = Depends(validate_task_id)):
    """
    Get task - validation handled by dependency
    
    If task doesn't exist, dependency raises 404
    """
    return task


@app.put("/tasks/{task_id}")
def update_task(
    task: dict = Depends(validate_task_id),
    title: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Update task - reuses same validation dependency
    """
    if title:
        task["title"] = title
    if status:
        task["status"] = status
    return task


# ============================================================
# CONCEPT 3: Authentication Dependency
# ============================================================

def get_api_key(x_api_key: Annotated[str, Header()]):
    """
    Dependency to extract API key from header
    """
    return x_api_key


def get_current_user(api_key: str = Depends(get_api_key)):
    """
    Dependency to authenticate user via API key
    
    Depends on get_api_key (chained dependency)
    """
    for username, user in users_db.items():
        if user["api_key"] == api_key:
            return user
    
    raise HTTPException(
        status_code=401,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "ApiKey"}
    )


@app.get("/users/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user info
    
    Requires valid API key header
    Test with: X-API-Key: admin-key-12345
    """
    return {
        "username": current_user["username"],
        "role": current_user["role"]
    }


# ============================================================
# CONCEPT 4: Role-Based Authorization Dependency
# ============================================================

def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency that requires admin role
    
    Chains with get_current_user
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


@app.delete("/tasks/{task_id}")
def delete_task(
    task: dict = Depends(validate_task_id),
    admin: dict = Depends(require_admin)  # Must be admin
):
    """
    Delete task - requires admin role
    
    Headers: X-API-Key: admin-key-12345
    """
    task_id = task["id"]
    del tasks_db[task_id]
    return {"message": f"Task {task_id} deleted by {admin['username']}"}


# ============================================================
# CONCEPT 5: Class-Based Dependencies
# ============================================================

class Pagination:
    """
    Class-based dependency for pagination
    
    Benefits:
    - Can store state
    - More complex initialization
    - Better for configuration
    """
    def __init__(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        sort_by: Optional[str] = Query(default=None),
        sort_order: str = Query(default="asc", pattern="^(asc|desc)$")
    ):
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.sort_order = sort_order


@app.get("/v2/tasks")
def list_tasks_v2(pagination: Pagination = Depends()):
    """
    List tasks with class-based pagination
    
    Note: Depends() without argument uses the class __init__
    """
    tasks = list(tasks_db.values())
    
    # Apply sorting
    if pagination.sort_by:
        reverse = pagination.sort_order == "desc"
        tasks = sorted(tasks, key=lambda x: x.get(pagination.sort_by, ""), reverse=reverse)
    
    # Apply pagination
    start = pagination.skip
    end = start + pagination.limit
    
    return {
        "pagination": {
            "skip": pagination.skip,
            "limit": pagination.limit,
            "sort_by": pagination.sort_by,
            "sort_order": pagination.sort_order
        },
        "total": len(tasks_db),
        "tasks": tasks[start:end]
    }


# ============================================================
# CONCEPT 6: Callable Class Dependency
# ============================================================

class ApiKeyChecker:
    """
    Callable class - uses __call__ method
    
    Useful when you need to configure the dependency
    """
    def __init__(self, required_role: str = None):
        self.required_role = required_role
    
    def __call__(self, x_api_key: Annotated[str, Header()]):
        # Find user by API key
        user = None
        for u in users_db.values():
            if u["api_key"] == x_api_key:
                user = u
                break
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Check role if required
        if self.required_role and user["role"] != self.required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{self.required_role}' required"
            )
        
        return user


# Create instances with different configurations
check_any_user = ApiKeyChecker()
check_admin = ApiKeyChecker(required_role="admin")


@app.get("/admin/stats")
def admin_stats(user: dict = Depends(check_admin)):
    """
    Admin-only endpoint using callable class
    """
    return {
        "admin": user["username"],
        "total_tasks": len(tasks_db),
        "total_users": len(users_db)
    }


# ============================================================
# CONCEPT 7: Dependencies with Yield (Resource Cleanup)
# ============================================================

def get_db():
    """
    Dependency with yield - ensures cleanup
    
    Code before yield: Setup (runs before endpoint)
    Code after yield: Cleanup (runs after endpoint, even on error)
    """
    db = FakeDatabase()
    db.connect()
    try:
        yield db  # This is what the endpoint receives
    finally:
        db.disconnect()  # Always runs - cleanup


@app.get("/db/tasks")
def get_tasks_from_db(db: FakeDatabase = Depends(get_db)):
    """
    Endpoint using database dependency
    
    Check console: you'll see connect/disconnect logs
    """
    return {
        "db_connected": db.connected,
        "connection_id": db.connection_id,
        "tasks": list(tasks_db.values())
    }


# ============================================================
# CONCEPT 8: Nested/Chained Dependencies
# ============================================================

def get_request_id():
    """Generate unique request ID"""
    return f"req-{secrets.token_hex(8)}"


def get_request_context(
    request_id: str = Depends(get_request_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency that depends on other dependencies
    
    Creates a request context with user and request ID
    """
    return {
        "request_id": request_id,
        "user": current_user["username"],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/v2/tasks")
def create_task_v2(
    title: str,
    context: dict = Depends(get_request_context)
):
    """
    Create task with full request context
    
    Chains: get_request_id + get_current_user → get_request_context
    """
    new_id = max(tasks_db.keys()) + 1
    new_task = {
        "id": new_id,
        "title": title,
        "status": "pending",
        "owner": context["user"],
        "created_at": context["timestamp"],
        "request_id": context["request_id"]
    }
    tasks_db[new_id] = new_task
    
    return {
        "message": "Task created",
        "task": new_task,
        "context": context
    }


# ============================================================
# CONCEPT 9: Path Operation Dependencies
# ============================================================
# Dependencies that don't return values, just perform checks

def verify_rate_limit():
    """
    Dependency for rate limiting (simplified)
    
    In real app, would check request count per IP/user
    """
    # Simulated rate limit check
    requests_remaining = 99
    if requests_remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    # No return needed - just a check


def log_request():
    """
    Dependency for logging (side effect only)
    """
    print(f"[LOG] Request at {datetime.now().isoformat()}")


@app.get(
    "/limited/tasks",
    dependencies=[Depends(verify_rate_limit), Depends(log_request)]
)
def list_tasks_limited():
    """
    Endpoint with path operation dependencies
    
    Dependencies run but their return values aren't used
    """
    return {"tasks": list(tasks_db.values())}


# ============================================================
# CONCEPT 10: Global Dependencies
# ============================================================
# Applied to ALL endpoints in the app

def global_rate_limit():
    """Global rate limit check"""
    pass  # Simplified


def verify_api_version(
    x_api_version: Annotated[Optional[str], Header()] = None
):
    """Check API version header"""
    if x_api_version and x_api_version not in ["1.0", "2.0"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported API version: {x_api_version}"
        )


# Note: In a real app, you'd add global dependencies like this:
# app = FastAPI(dependencies=[Depends(global_rate_limit), Depends(verify_api_version)])


# ============================================================
# CONCEPT 11: Dependency Overrides (for testing)
# ============================================================
# Demonstrated here, used in tests to mock dependencies

def get_settings():
    """Get application settings"""
    return {
        "app_name": "Task Manager",
        "debug": False,
        "max_tasks": 1000
    }


@app.get("/settings")
def read_settings(settings: dict = Depends(get_settings)):
    """
    Get settings - can be overridden in tests
    
    In tests:
    app.dependency_overrides[get_settings] = lambda: {"debug": True}
    """
    return settings


# ============================================================
# CONCEPT 12: Common Patterns Combined
# ============================================================

class CommonQueryParams:
    """Reusable query parameters"""
    def __init__(
        self,
        q: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ):
        self.q = q
        self.skip = skip
        self.limit = limit


class TaskFilters:
    """Task-specific filters"""
    def __init__(
        self,
        status: Optional[str] = None,
        owner: Optional[str] = None
    ):
        self.status = status
        self.owner = owner


@app.get("/search/tasks")
def search_tasks(
    common: CommonQueryParams = Depends(),
    filters: TaskFilters = Depends(),
    user: dict = Depends(get_current_user)
):
    """
    Search tasks with multiple dependencies
    
    Combines:
    - CommonQueryParams (pagination + search)
    - TaskFilters (status, owner)
    - Authentication
    """
    results = list(tasks_db.values())
    
    # Apply filters
    if filters.status:
        results = [t for t in results if t["status"] == filters.status]
    if filters.owner:
        results = [t for t in results if t["owner"] == filters.owner]
    
    # Apply search
    if common.q:
        results = [t for t in results if common.q.lower() in t["title"].lower()]
    
    # Apply pagination
    total = len(results)
    results = results[common.skip: common.skip + common.limit]
    
    return {
        "user": user["username"],
        "search": common.q,
        "filters": {"status": filters.status, "owner": filters.owner},
        "pagination": {"skip": common.skip, "limit": common.limit},
        "total": total,
        "tasks": results
    }


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 10 - Dependency Injection",
        "concepts": [
            "Depends() - Basic dependency injection",
            "Function dependencies",
            "Class-based dependencies",
            "Callable class dependencies",
            "Dependencies with yield (cleanup)",
            "Nested/chained dependencies",
            "Path operation dependencies",
            "Global dependencies"
        ],
        "test_with_api_key": {
            "admin": "X-API-Key: admin-key-12345",
            "user": "X-API-Key: user1-key-67890"
        },
        "endpoints": {
            "basic": [
                "GET /tasks - Pagination dependency",
                "GET /tasks/{id} - Validation dependency"
            ],
            "auth": [
                "GET /users/me - Auth dependency",
                "DELETE /tasks/{id} - Admin required"
            ],
            "class_based": [
                "GET /v2/tasks - Class pagination",
                "GET /admin/stats - Callable class"
            ],
            "advanced": [
                "GET /db/tasks - Yield dependency",
                "POST /v2/tasks - Chained dependencies",
                "GET /limited/tasks - Path dependencies",
                "GET /search/tasks - Multiple dependencies"
            ]
        }
    }
