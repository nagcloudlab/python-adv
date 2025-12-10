# Level 4: Request Body (Pydantic Models)

## Learning Objectives
- Define request body using Pydantic BaseModel
- Use POST, PUT, PATCH, DELETE methods
- Create required and optional fields
- Build nested models
- Perform partial updates with PATCH
- Combine body with path and query parameters
- Add model examples for Swagger UI

---

## Setup Instructions

```bash
cd level_04_request_body
pip install -r requirements.txt
uvicorn main:app --reload
```

**Testing Tip:** Use Swagger UI at http://127.0.0.1:8000/docs to test POST/PUT/PATCH requests interactively.

---

## Key Concepts

### 1. Basic Pydantic Model
```python
from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str                          # Required
    description: Optional[str] = None   # Optional
    priority: int = 1                   # Optional with default
```

### 2. Using Model in Endpoint
```python
@app.post("/tasks")
def create_task(task: TaskCreate):
    # task is automatically validated
    return {"title": task.title, "priority": task.priority}
```

**Request Body (JSON):**
```json
{
    "title": "Learn FastAPI",
    "description": "Complete the tutorial",
    "priority": 2
}
```

### 3. HTTP Methods Overview

| Method | Purpose | Has Body? | Idempotent? |
|--------|---------|-----------|-------------|
| `POST` | Create new resource | ✅ Yes | ❌ No |
| `PUT` | Full update/replace | ✅ Yes | ✅ Yes |
| `PATCH` | Partial update | ✅ Yes | ✅ Yes |
| `DELETE` | Remove resource | ❌ Usually no | ✅ Yes |

### 4. Nested Models
```python
class Tag(BaseModel):
    name: str
    color: str = "blue"

class Assignee(BaseModel):
    username: str
    email: str

class TaskWithNested(BaseModel):
    title: str
    tags: List[Tag] = []
    assignee: Optional[Assignee] = None
```

**Request Body:**
```json
{
    "title": "Complex Task",
    "tags": [
        {"name": "urgent", "color": "red"},
        {"name": "backend"}
    ],
    "assignee": {
        "username": "john",
        "email": "john@example.com"
    }
}
```

### 5. PUT vs PATCH

**PUT - Full Update (all fields required/defaulted):**
```python
class TaskUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1
    status: TaskStatus = TaskStatus.pending

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    # Replaces entire resource
    pass
```

**PATCH - Partial Update (all fields optional):**
```python
class TaskPartialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[TaskStatus] = None

@app.patch("/tasks/{task_id}")
def partial_update(task_id: int, task: TaskPartialUpdate):
    # Update only provided fields
    update_data = task.model_dump(exclude_unset=True)
    # apply update_data...
```

### 6. Combining Body + Path + Query
```python
@app.post("/tasks/{task_id}/comments")
def add_comment(
    task_id: int,           # Path parameter
    comment: CommentCreate, # Request body
    notify: bool = False    # Query parameter
):
    pass
```

**URL:** `POST /tasks/1/comments?notify=true`  
**Body:** `{"text": "Great!", "author": "john"}`

### 7. Bulk Create (List of Models)
```python
@app.post("/tasks/bulk")
def create_bulk(tasks: List[TaskCreate]):
    for task in tasks:
        # create each task
    pass
```

**Request Body:**
```json
[
    {"title": "Task 1", "priority": 1},
    {"title": "Task 2", "priority": 2}
]
```

### 8. Model Examples (for Swagger UI)
```python
class TaskWithExample(BaseModel):
    title: str
    priority: int = 1
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Sample Task",
                    "priority": 2
                }
            ]
        }
    }
```

---

## Pydantic Model Methods

| Method | Description |
|--------|-------------|
| `task.model_dump()` | Convert model to dictionary |
| `task.model_dump(exclude_unset=True)` | Only fields that were set |
| `task.model_dump(exclude={"password"})` | Exclude specific fields |
| `task.model_dump_json()` | Convert to JSON string |

---

## Validation Examples

### Automatic Type Validation
```json
// ❌ Invalid - title must be string
{"title": 123, "priority": 1}

// ❌ Invalid - priority must be int
{"title": "Task", "priority": "high"}

// ✅ Valid
{"title": "Task", "priority": 1}
```

### Enum Validation
```json
// ❌ Invalid status
{"title": "Task", "status": "invalid"}

// ✅ Valid status
{"title": "Task", "status": "pending"}
```

---

## Test Scenarios (Use Swagger UI)

### 1. Create Task (POST)
```
POST /tasks
Body: {"title": "Test Task", "priority": 2}
```

### 2. Update Task (PUT)
```
PUT /tasks/1
Body: {"title": "Updated", "status": "completed"}
```

### 3. Partial Update (PATCH)
```
PATCH /tasks/1
Body: {"status": "completed"}
```

### 4. Delete Task (DELETE)
```
DELETE /tasks/1
```

### 5. Nested Model (POST)
```
POST /tasks/detailed
Body: {
    "title": "Complex Task",
    "tags": [{"name": "urgent", "color": "red"}],
    "assignee": {"username": "john", "email": "john@example.com"}
}
```

### 6. Bulk Create (POST)
```
POST /tasks/bulk
Body: [
    {"title": "Task 1"},
    {"title": "Task 2", "priority": 3}
]
```

---

## Exercises

### Exercise 1: User Registration
Create `POST /users` with model:
- `username`: Required string
- `email`: Required string
- `password`: Required string
- `full_name`: Optional string
- `age`: Optional int

### Exercise 2: Product with Variants
Create nested models:
- `Variant`: size (str), color (str), stock (int)
- `Product`: name (str), price (float), variants (List[Variant])

Create `POST /products` endpoint.

### Exercise 3: Order System
Create:
- `OrderItem`: product_id (int), quantity (int)
- `Order`: customer_name (str), items (List[OrderItem])
- `OrderUpdate`: status only (for PATCH)

Endpoints:
- `POST /orders`
- `PATCH /orders/{id}`

### Exercise 4: Bulk Operations
Create `DELETE /tasks/bulk` that accepts:
```json
{"task_ids": [1, 2, 3]}
```

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `422 - field required` | Missing required field | Include all required fields |
| `422 - value is not valid` | Wrong type | Check field types |
| `422 - not a valid enumeration` | Invalid enum value | Use valid enum value |
| Body not parsed | Missing `Content-Type` | Set `Content-Type: application/json` |

---

## What's Next?
**Level 5: Response Models** - Control what data is returned, exclude sensitive fields, and document response schemas.
