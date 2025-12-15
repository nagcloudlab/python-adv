# Level 1: Hello FastAPI

## Learning Objectives
- Install FastAPI and Uvicorn
- Create your first FastAPI application
- Define GET endpoints
- Understand automatic JSON conversion
- Explore auto-generated API documentation

---

## Setup Instructions

### Step 1: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
uvicorn main:app --reload
```

### Step 4: Test the Endpoints

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | Root endpoint |
| http://127.0.0.1:8000/health | Health check |
| http://127.0.0.1:8000/about | About API |
| http://127.0.0.1:8000/tasks | List tasks |
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |

---

## Key Concepts

### 1. FastAPI Instance
```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="API Description",
    version="1.0.0"
)
```

### 2. Route Decorators
```python
@app.get("/path")      # HTTP GET
@app.post("/path")     # HTTP POST (Level 4)
@app.put("/path")      # HTTP PUT (Level 4)
@app.delete("/path")   # HTTP DELETE (Level 4)
```

### 3. Automatic JSON Response
```python
@app.get("/example")
def example():
    return {"key": "value"}  # Automatically converted to JSON
```

### 4. Uvicorn Command Explained
```bash
uvicorn main:app --reload
```
- `main` → Python file name (main.py)
- `app` → FastAPI instance variable
- `--reload` → Auto-restart on code changes (development only)

---

## Exercises

### Exercise 1: Add New Endpoint
Create a `/version` endpoint that returns:
```json
{"version": "1.0.0", "release_date": "2024-01-01"}
```

### Exercise 2: Add Status Endpoint
Create a `/status` endpoint that returns:
```json
{"database": "connected", "cache": "active", "uptime": "2 hours"}
```

### Exercise 3: Modify Swagger Info
Change the `title`, `description`, and `version` in FastAPI() constructor and observe changes in /docs

---

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | FastAPI not installed | Run `pip install fastapi` |
| `ModuleNotFoundError: No module named 'uvicorn'` | Uvicorn not installed | Run `pip install uvicorn` |
| `Address already in use` | Port 8000 occupied | Use `--port 8001` or stop other process |
| `Error loading ASGI app` | Wrong app name | Check `main:app` matches your file and variable |

---

## What's Next?
**Level 2: Path Parameters** - Learn to create dynamic URLs like `/tasks/1`, `/users/john`
