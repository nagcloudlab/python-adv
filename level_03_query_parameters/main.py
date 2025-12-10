"""
Level 3: Query Parameters
=========================
Concepts Covered:
    - Query parameters basics (?key=value)
    - Required vs Optional parameters
    - Default values
    - Type conversion (int, bool, float)
    - Multiple query parameters
    - List query parameters (?tag=a&tag=b)
    - Combining path and query parameters

Run Command:
    uvicorn main:app --reload

Test URLs:
    http://127.0.0.1:8000/tasks
    http://127.0.0.1:8000/tasks?skip=0&limit=5
    http://127.0.0.1:8000/tasks?status=completed
    http://127.0.0.1:8000/search?q=API
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from typing import Optional, List

app = FastAPI(
    title="Task Manager API - Level 3",
    description="Learning Query Parameters",
    version="3.0.0"
)

# ============================================================
# Sample Data
# ============================================================

tasks_db = [
    {"id": 1, "title": "Learn FastAPI Basics", "status": "completed", "priority": 1, "tags": ["python", "api"]},
    {"id": 2, "title": "Build REST API", "status": "in_progress", "priority": 2, "tags": ["python", "backend"]},
    {"id": 3, "title": "Write Unit Tests", "status": "pending", "priority": 1, "tags": ["testing"]},
    {"id": 4, "title": "Setup Database", "status": "pending", "priority": 3, "tags": ["database", "backend"]},
    {"id": 5, "title": "Deploy Application", "status": "pending", "priority": 2, "tags": ["devops"]},
    {"id": 6, "title": "API Documentation", "status": "in_progress", "priority": 1, "tags": ["docs", "api"]},
    {"id": 7, "title": "Code Review", "status": "completed", "priority": 2, "tags": ["review"]},
    {"id": 8, "title": "Performance Testing", "status": "pending", "priority": 3, "tags": ["testing", "performance"]},
]


# ============================================================
# CONCEPT 1: Query Parameters with Default Values
# ============================================================
# Parameters not in path {} are automatically query parameters
# Default values make them optional

@app.get("/tasks")
def list_tasks(skip: int = 0, limit: int = 10):
    """
    List tasks with pagination
    
    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 10)
    
    Examples:
    - /tasks              → First 10 tasks
    - /tasks?limit=5      → First 5 tasks
    - /tasks?skip=2       → Skip first 2, return next 10
    - /tasks?skip=2&limit=3 → Skip 2, return 3
    """
    return {
        "skip": skip,
        "limit": limit,
        "total": len(tasks_db),
        "tasks": tasks_db[skip: skip + limit]
    }


# ============================================================
# CONCEPT 2: Optional Query Parameters
# ============================================================
# Use Optional[type] with default None for truly optional params

@app.get("/tasks/filter")
def filter_tasks(status: Optional[str] = None):
    """
    Filter tasks by status (optional)
    
    - If status provided: filter by that status
    - If status not provided: return all tasks
    
    Examples:
    - /tasks/filter                    → All tasks
    - /tasks/filter?status=completed   → Only completed
    - /tasks/filter?status=pending     → Only pending
    """
    if status:
        filtered = [t for t in tasks_db if t["status"] == status]
        return {"filter": status, "count": len(filtered), "tasks": filtered}
    
    return {"filter": None, "count": len(tasks_db), "tasks": tasks_db}


# ============================================================
# CONCEPT 3: Required Query Parameters
# ============================================================
# No default value = Required parameter

@app.get("/search")
def search_tasks(q: str):
    """
    Search tasks - 'q' is REQUIRED
    
    - No default value means parameter is mandatory
    - Omitting ?q= will return 422 error
    
    Examples:
    - /search?q=API       → Search for "API"
    - /search?q=test      → Search for "test"
    - /search             → ERROR: q is required
    """
    results = [
        t for t in tasks_db 
        if q.lower() in t["title"].lower()
    ]
    return {
        "query": q,
        "count": len(results),
        "results": results
    }


# ============================================================
# CONCEPT 4: Multiple Query Parameters with Different Types
# ============================================================

@app.get("/tasks/advanced")
def advanced_filter(
    status: Optional[str] = None,
    priority: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    sort_by_priority: bool = False
):
    """
    Advanced filtering with multiple parameters
    
    Query Parameters:
    - status: Filter by status (optional)
    - priority: Filter by priority 1-3 (optional)
    - skip: Pagination offset (default: 0)
    - limit: Pagination limit (default: 10)
    - sort_by_priority: Sort results by priority (default: false)
    
    Examples:
    - /tasks/advanced?status=pending
    - /tasks/advanced?priority=1
    - /tasks/advanced?status=pending&priority=1
    - /tasks/advanced?sort_by_priority=true
    - /tasks/advanced?status=pending&sort_by_priority=true&limit=5
    """
    results = tasks_db.copy()
    
    # Apply filters
    if status:
        results = [t for t in results if t["status"] == status]
    
    if priority:
        results = [t for t in results if t["priority"] == priority]
    
    # Apply sorting
    if sort_by_priority:
        results = sorted(results, key=lambda x: x["priority"])
    
    # Apply pagination
    paginated = results[skip: skip + limit]
    
    return {
        "filters": {
            "status": status,
            "priority": priority
        },
        "pagination": {
            "skip": skip,
            "limit": limit
        },
        "sorted": sort_by_priority,
        "total_filtered": len(results),
        "tasks": paginated
    }


# ============================================================
# CONCEPT 5: Boolean Query Parameters
# ============================================================
# Boolean accepts: true, false, 1, 0, yes, no, on, off

@app.get("/tasks/search")
def search_with_options(
    q: str,
    case_sensitive: bool = False,
    include_completed: bool = True
):
    """
    Search with boolean options
    
    Boolean values accepted:
    - true, false
    - 1, 0
    - yes, no
    - on, off
    
    Examples:
    - /tasks/search?q=api
    - /tasks/search?q=API&case_sensitive=true
    - /tasks/search?q=test&include_completed=false
    - /tasks/search?q=test&case_sensitive=1&include_completed=0
    """
    results = tasks_db.copy()
    
    # Exclude completed if requested
    if not include_completed:
        results = [t for t in results if t["status"] != "completed"]
    
    # Apply search
    if case_sensitive:
        results = [t for t in results if q in t["title"]]
    else:
        results = [t for t in results if q.lower() in t["title"].lower()]
    
    return {
        "query": q,
        "case_sensitive": case_sensitive,
        "include_completed": include_completed,
        "count": len(results),
        "results": results
    }


# ============================================================
# CONCEPT 6: List Query Parameters
# ============================================================
# Same parameter multiple times: ?tag=a&tag=b&tag=c

@app.get("/tasks/by-tags")
def filter_by_tags(tag: List[str] = []):
    """
    Filter tasks by multiple tags
    
    Pass same parameter multiple times for list:
    - /tasks/by-tags?tag=python
    - /tasks/by-tags?tag=python&tag=api
    - /tasks/by-tags?tag=testing&tag=backend&tag=api
    
    Returns tasks that have ANY of the specified tags
    """
    if not tag:
        return {"tags": [], "tasks": tasks_db}
    
    results = [
        t for t in tasks_db 
        if any(tg in t["tags"] for tg in tag)
    ]
    
    return {
        "tags": tag,
        "count": len(results),
        "tasks": results
    }


# ============================================================
# CONCEPT 7: Combining Path and Query Parameters
# ============================================================

@app.get("/users/{username}/tasks")
def get_user_tasks(
    username: str,
    status: Optional[str] = None,
    limit: int = 10
):
    """
    Get tasks for a specific user with optional filters
    
    Path Parameter:
    - username: The user's username
    
    Query Parameters:
    - status: Filter by status (optional)
    - limit: Max results (default: 10)
    
    Examples:
    - /users/john/tasks
    - /users/john/tasks?status=pending
    - /users/john/tasks?status=completed&limit=5
    """
    # Simulate user's tasks (in real app, filter from DB)
    user_tasks = tasks_db[:5]  # Pretend these belong to user
    
    if status:
        user_tasks = [t for t in user_tasks if t["status"] == status]
    
    return {
        "username": username,
        "filter_status": status,
        "limit": limit,
        "tasks": user_tasks[:limit]
    }


# ============================================================
# CONCEPT 8: Required with Explicit None Check
# ============================================================

@app.get("/tasks/range")
def get_tasks_range(
    min_priority: int,
    max_priority: int,
    status: Optional[str] = None
):
    """
    Get tasks within priority range
    
    Required Parameters:
    - min_priority: Minimum priority (required)
    - max_priority: Maximum priority (required)
    
    Optional Parameters:
    - status: Filter by status
    
    Examples:
    - /tasks/range?min_priority=1&max_priority=2
    - /tasks/range?min_priority=1&max_priority=3&status=pending
    """
    results = [
        t for t in tasks_db
        if min_priority <= t["priority"] <= max_priority
    ]
    
    if status:
        results = [t for t in results if t["status"] == status]
    
    return {
        "range": {"min": min_priority, "max": max_priority},
        "status": status,
        "count": len(results),
        "tasks": results
    }


# ============================================================
# CONCEPT 9: Float Query Parameters
# ============================================================

@app.get("/budget/filter")
def filter_by_budget(
    min_amount: float = 0.0,
    max_amount: float = 1000000.0
):
    """
    Filter by budget range (demonstrating float parameters)
    
    Examples:
    - /budget/filter?min_amount=100.50
    - /budget/filter?max_amount=500
    - /budget/filter?min_amount=100&max_amount=999.99
    """
    return {
        "min_amount": min_amount,
        "max_amount": max_amount,
        "message": f"Filtering items with budget between {min_amount} and {max_amount}"
    }


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root - Available endpoints"""
    return {
        "message": "Level 3 - Query Parameters",
        "endpoints": [
            "GET /tasks?skip=0&limit=10",
            "GET /tasks/filter?status=pending",
            "GET /search?q=keyword (required)",
            "GET /tasks/advanced?status=...&priority=...&sort_by_priority=true",
            "GET /tasks/search?q=...&case_sensitive=false&include_completed=true",
            "GET /tasks/by-tags?tag=python&tag=api",
            "GET /users/{username}/tasks?status=...&limit=10",
            "GET /tasks/range?min_priority=1&max_priority=3",
            "GET /budget/filter?min_amount=0&max_amount=1000"
        ]
    }
