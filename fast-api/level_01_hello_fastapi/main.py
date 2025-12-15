"""
Level 1: Hello FastAPI
======================
Concepts Covered:
    - FastAPI installation
    - Creating application instance
    - Defining GET endpoints
    - Running with Uvicorn
    - Automatic API documentation

Run Command:
    uvicorn main:app --reload

Access URLs:
    http://127.0.0.1:8000           → Root endpoint
    http://127.0.0.1:8000/health    → Health check
    http://127.0.0.1:8000/about     → About API
    http://127.0.0.1:8000/docs      → Swagger UI (Interactive)
    http://127.0.0.1:8000/redoc     → ReDoc (Alternative docs)
"""

from fastapi import FastAPI

# ============================================================
# STEP 1: Create FastAPI Application Instance
# ============================================================
# FastAPI() creates the main application object
# Parameters:
#   - title: API name shown in documentation
#   - description: API description in docs
#   - version: API version number

app = FastAPI(
    title="Task Manager API",
    description="A simple Task Management API for learning FastAPI",
    version="1.0.0"
)


# ============================================================
# STEP 2: Define Endpoints using Decorators
# ============================================================
# @app.get("/path") - Handles HTTP GET requests
# Function below decorator handles the request and returns response
# Return value is automatically converted to JSON

@app.get("/")
def root():
    """
    Root endpoint - Welcome message
    
    This is the entry point of our API.
    Returns a simple JSON greeting.
    """
    return {"message": "Welcome to Task Manager API"}


@app.get("/health")
def health_check():
    """
    Health check endpoint
    
    Used by monitoring systems to verify API is running.
    Common in production deployments.
    """
    return {
        "status": "healthy",
        "api": "Task Manager",
        "version": "1.0.0"
    }


@app.get("/about")
def about():
    """
    About endpoint
    
    Returns metadata about the API.
    The docstring you're reading becomes the endpoint description in docs!
    """
    return {
        "name": "Task Manager API",
        "version": "1.0.0",
        "framework": "FastAPI",
        "author": "Training Team"
    }


# ============================================================
# STEP 3: Sample Data Endpoint
# ============================================================
# Returning a list of dictionaries (will be JSON array)

@app.get("/tasks")
def list_tasks():
    """
    List all tasks
    
    Returns a sample list of tasks.
    In later levels, this will come from a database.
    """
    tasks = [
        {"id": 1, "title": "Learn FastAPI", "status": "in_progress"},
        {"id": 2, "title": "Build REST API", "status": "pending"},
        {"id": 3, "title": "Write Documentation", "status": "completed"}
    ]
    return {"tasks": tasks, "count": len(tasks)}


# ============================================================
# UNDERSTANDING THE CODE
# ============================================================
"""
Key Concepts:

1. DECORATORS (@app.get, @app.post, etc.)
   - @app.get("/path") → HTTP GET method
   - @app.post("/path") → HTTP POST method (Level 4)
   - @app.put("/path")  → HTTP PUT method (Level 4)
   - @app.delete("/path") → HTTP DELETE method (Level 4)

2. FUNCTION RETURN → JSON
   - dict   → JSON object: {"key": "value"}
   - list   → JSON array: [1, 2, 3]
   - str    → JSON string: "hello"
   - int    → JSON number: 42
   - bool   → JSON boolean: true/false
   - None   → JSON null

3. AUTOMATIC DOCUMENTATION
   - Function docstrings become endpoint descriptions
   - Swagger UI at /docs is interactive (try it!)
   - ReDoc at /redoc is read-only documentation

4. UVICORN SERVER
   - uvicorn main:app --reload
   - main = filename (main.py)
   - app = FastAPI instance variable name
   - --reload = auto-restart on code changes (dev only)
"""
