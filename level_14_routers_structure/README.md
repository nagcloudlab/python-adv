# Level 14: APIRouter & Project Structure

## Learning Objectives
- Organize endpoints with `APIRouter`
- Structure a multi-file FastAPI project
- Share dependencies across routers
- Centralize configuration with Pydantic Settings
- Separate schemas (Pydantic) from models (DB)
- Apply router-level dependencies

---

## Setup Instructions

```bash
cd level_14_routers_structure
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Project Structure

```
level_14_routers_structure/
├── main.py                 # App entry point
├── requirements.txt
└── app/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── config.py       # Settings
    │   └── dependencies.py # Shared dependencies
    ├── routers/
    │   ├── __init__.py
    │   ├── tasks.py        # /tasks endpoints
    │   ├── users.py        # /users endpoints
    │   └── admin.py        # /admin endpoints
    ├── models/
    │   ├── __init__.py
    │   └── database.py     # Data layer
    └── schemas/
        ├── __init__.py
        ├── task.py         # Task schemas
        └── user.py         # User schemas
```

---

## Key Concepts

### 1. Creating a Router
```python
# app/routers/tasks.py
from fastapi import APIRouter

router = APIRouter()

@router.get("")
def list_tasks():
    return {"tasks": [...]}

@router.post("")
def create_task(task: TaskCreate):
    return {"id": 1}
```

### 2. Including Router in App
```python
# main.py
from fastapi import FastAPI
from app.routers import tasks, users, admin

app = FastAPI()

app.include_router(
    tasks.router,
    prefix="/tasks",     # All routes start with /tasks
    tags=["Tasks"]       # Swagger UI grouping
)

app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)
```

### 3. Router with Default Dependencies
```python
# app/routers/admin.py
from fastapi import APIRouter, Depends
from app.core.dependencies import require_admin

# ALL endpoints require admin
router = APIRouter(
    dependencies=[Depends(require_admin)]
)

@router.get("/dashboard")
def dashboard():
    # Only admins can access
    return {"stats": {...}}
```

### 4. Centralized Configuration
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "My API"
    DEBUG: bool = True
    API_KEY: str = "secret"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# Usage
from app.core.config import settings
print(settings.APP_NAME)
```

### 5. Shared Dependencies
```python
# app/core/dependencies.py
from fastapi import Depends, HTTPException

class Pagination:
    def __init__(self, page: int = 1, size: int = 10):
        self.skip = (page - 1) * size
        self.limit = size

def get_current_user(token: str = Header()):
    # Validate token...
    return user

def require_admin(user = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(403)
    return user
```

### 6. Schemas vs Models

**Schemas (Pydantic)** - Request/Response validation
```python
# app/schemas/task.py
class TaskCreate(BaseModel):
    title: str
    description: Optional[str]

class TaskResponse(BaseModel):
    id: int
    title: str
```

**Models (Database)** - Data storage
```python
# app/models/database.py (or SQLAlchemy models)
tasks_db = {
    1: {"id": 1, "title": "..."}
}
```

---

## API Endpoints

### Tasks (`/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List tasks (paginated) |
| GET | `/tasks/{id}` | Get task by ID |
| POST | `/tasks` | Create task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| GET | `/tasks/my/tasks` | Get my tasks |

### Users (`/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get my profile |
| PUT | `/users/me` | Update my profile |
| GET | `/users/{id}` | Get user by ID |
| GET | `/users` | List all users |

### Admin (`/admin`) - Admin Only
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard` | Statistics |
| GET | `/admin/users` | List all users |
| PUT | `/admin/users/{id}/activate` | Activate user |
| PUT | `/admin/users/{id}/deactivate` | Deactivate user |
| DELETE | `/admin/users/{id}` | Delete user |
| GET | `/admin/tasks` | List all tasks |
| DELETE | `/admin/tasks/{id}` | Force delete task |

---

## Authentication

This API uses simplified header-based auth:

| Header | Value | Role |
|--------|-------|------|
| X-User-Id | `admin` | Admin |
| X-User-Id | `user1` | Regular user |
| X-User-Id | `user2` | Inactive user |

### Example
```bash
# As regular user
curl -H "X-User-Id: user1" http://localhost:8000/users/me

# As admin
curl -H "X-User-Id: admin" http://localhost:8000/admin/dashboard
```

---

## Testing

### List Tasks
```bash
curl -H "X-User-Id: user1" "http://localhost:8000/tasks?page=1&size=10"
```

### Create Task
```bash
curl -X POST -H "X-User-Id: user1" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "priority": 3}' \
  http://localhost:8000/tasks
```

### Admin Dashboard
```bash
curl -H "X-User-Id: admin" http://localhost:8000/admin/dashboard
```

---

## Exercises

### Exercise 1: Add Projects Router
Create `/projects` router with:
- CRUD endpoints
- Nested tasks: `/projects/{id}/tasks`

### Exercise 2: Add Tags Router
Create `/tags` router:
- List, create, delete tags
- Add tags to tasks

### Exercise 3: Environment Config
- Create `.env` file
- Override settings via environment
- Add database URL setting

### Exercise 4: Versioned API
- Create `/api/v1/` prefix
- Create `/api/v2/` with different behavior

---

## Best Practices

1. **One router per resource** - tasks.py, users.py
2. **Prefix in main.py** - Not in router
3. **Tags for Swagger** - Group related endpoints
4. **Shared dependencies** - In core/dependencies.py
5. **Separate schemas** - From database models
6. **Centralized config** - Use pydantic-settings

---

## Common Patterns

### Router with Multiple Tags
```python
router = APIRouter(
    prefix="/items",
    tags=["Items", "Inventory"]
)
```

### Nested Routers
```python
# In main.py
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(tasks.router, prefix="/tasks")
api_router.include_router(users.router, prefix="/users")

app.include_router(api_router)
# Results in: /api/v1/tasks, /api/v1/users
```

### Router-Level Response Model
```python
router = APIRouter(
    responses={404: {"description": "Not found"}}
)
```

---

## What's Next?
**Level 15: Database Integration (SQLAlchemy)** - Connect to real databases with SQLAlchemy ORM.
