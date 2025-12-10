# Level 2: Path Parameters

## Learning Objectives
- Create dynamic URLs using path parameters
- Apply type hints for automatic validation
- Use multiple path parameters in one endpoint
- Restrict values using Enum
- Understand path ordering (fixed vs dynamic)
- Handle file paths with `:path` converter

---

## Setup Instructions

```bash
cd level_02_path_parameters
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Key Concepts

### 1. Basic Path Parameter
```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):    # Type hint enables validation
    return {"task_id": task_id}
```

| URL | Result |
|-----|--------|
| `/tasks/1` | ✅ Returns task |
| `/tasks/abc` | ❌ Validation error |

### 2. String Path Parameter
```python
@app.get("/users/{username}")
def get_user(username: str):
    return {"username": username}
```

### 3. Multiple Path Parameters
```python
@app.get("/users/{username}/tasks/{task_id}")
def get_user_task(username: str, task_id: int):
    return {"username": username, "task_id": task_id}
```

### 4. Enum for Predefined Values
```python
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

@app.get("/tasks/status/{status}")
def get_by_status(status: TaskStatus):
    return {"status": status.value}
```

**Benefits:**
- Auto-validation (rejects invalid values)
- Swagger UI shows dropdown
- Self-documenting code

### 5. Path Order Matters! ⚠️
```python
# ✅ CORRECT ORDER
@app.get("/items/count")      # Fixed path FIRST
def count(): ...

@app.get("/items/{item_id}")  # Dynamic path SECOND
def get_item(item_id: int): ...

# ❌ WRONG ORDER - /items/count will never be reached
@app.get("/items/{item_id}")  # This catches "count" as item_id
def get_item(item_id: int): ...

@app.get("/items/count")      # Never reached!
def count(): ...
```

### 6. File Path Parameter
```python
@app.get("/files/{file_path:path}")
def get_file(file_path: str):
    return {"file": file_path}
```

| URL | file_path value |
|-----|-----------------|
| `/files/doc.txt` | `doc.txt` |
| `/files/docs/report.pdf` | `docs/report.pdf` |

---

## Test URLs

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/tasks/1 | Get task by ID |
| http://127.0.0.1:8000/tasks/abc | Type validation error |
| http://127.0.0.1:8000/users/john | Get user by username |
| http://127.0.0.1:8000/users/john/tasks/1 | Get user's task |
| http://127.0.0.1:8000/tasks/status/pending | Tasks by status |
| http://127.0.0.1:8000/tasks/status/invalid | Enum validation error |
| http://127.0.0.1:8000/files/docs/report.pdf | File path parameter |
| http://127.0.0.1:8000/docs | Swagger UI |

---

## Supported Type Hints

| Type | Example | Valid Input |
|------|---------|-------------|
| `int` | `task_id: int` | `1`, `42`, `-5` |
| `float` | `price: float` | `9.99`, `10` |
| `str` | `name: str` | Any text |
| `bool` | `active: bool` | `true`, `false`, `1`, `0` |
| `Enum` | `status: TaskStatus` | Enum members only |

---

## Exercises

### Exercise 1: Product Endpoint
Create `/products/{product_id}` that returns product details:
```json
{"id": 1, "name": "Laptop", "price": 999.99}
```

### Exercise 2: Category Enum
Create an enum `Category` with values: `electronics`, `clothing`, `books`
Create `/products/category/{category}` endpoint

### Exercise 3: Nested Resources
Create `/departments/{dept_id}/employees/{emp_id}` endpoint

### Exercise 4: Order Matters
Create both endpoints and verify correct ordering:
- `/orders/pending` (fixed)
- `/orders/{order_id}` (dynamic)

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `422 Unprocessable Entity` | Wrong type (e.g., string for int) | Pass correct type |
| `404 Not Found` | Path order issue | Move fixed paths before dynamic |
| `value is not a valid enumeration member` | Invalid enum value | Use one of the defined enum values |

---

## What's Next?
**Level 3: Query Parameters** - Learn `?skip=0&limit=10` style parameters for filtering, pagination, and optional inputs.
