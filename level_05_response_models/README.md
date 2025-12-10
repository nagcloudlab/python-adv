# Level 5: Response Models

## Learning Objectives
- Use `response_model` to control API output
- Filter sensitive data (passwords, internal fields)
- Create separate input vs output models
- Use `response_model_exclude_unset`, `exclude`, `include`
- Handle multiple response types with `Union`
- Build wrapper models with metadata
- Create nested response models

---

## Setup Instructions

```bash
cd level_05_response_models
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Why Response Models?

### Problem: Exposing Sensitive Data
```python
# ❌ DANGEROUS - Returns everything including password!
@app.get("/users/{id}")
def get_user(id: int):
    return users_db[id]  # Has hashed_password field!
```

### Solution: Response Model
```python
# ✅ SAFE - Password automatically filtered
@app.get("/users/{id}", response_model=UserResponse)
def get_user(id: int):
    return users_db[id]  # Password filtered out!
```

---

## Key Concepts

### 1. Input vs Output Models
```python
# INPUT - for creating (has password)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str  # Accepted on input

# OUTPUT - for returning (NO password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    # No password field!

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    # Even if you return full dict with password,
    # FastAPI filters it based on response_model
    return {"id": 1, "username": user.username, ...}
```

### 2. List Response Model
```python
@app.get("/users", response_model=List[UserResponse])
def list_users():
    return list(users_db.values())  # Each filtered!
```

### 3. response_model_exclude_unset
```python
@app.get(
    "/tasks/{id}",
    response_model=TaskResponse,
    response_model_exclude_unset=True
)
def get_task(id: int):
    return tasks_db[id]
```

| Without exclude_unset | With exclude_unset |
|-----------------------|-------------------|
| `{"id": 1, "title": "Task", "description": null}` | `{"id": 1, "title": "Task"}` |

### 4. response_model_exclude
```python
@app.get(
    "/tasks/{id}/minimal",
    response_model=TaskResponse,
    response_model_exclude={"description", "created_at"}
)
def get_task_minimal(id: int):
    return tasks_db[id]
```

Excludes specific fields from response.

### 5. response_model_include
```python
@app.get(
    "/tasks/{id}/summary",
    response_model=TaskResponse,
    response_model_include={"id", "title", "status"}
)
def get_task_summary(id: int):
    return tasks_db[id]
```

Only includes specified fields (whitelist).

### 6. Union for Multiple Response Types
```python
class TaskResponse(BaseModel):
    id: int
    title: str
    status: str

class TaskNotFound(BaseModel):
    error: str
    task_id: int

@app.get("/tasks/{id}", response_model=Union[TaskResponse, TaskNotFound])
def get_task(id: int):
    if id in tasks_db:
        return tasks_db[id]
    return TaskNotFound(error="Not found", task_id=id)
```

### 7. Wrapper Response Model
```python
class TaskListResponse(BaseModel):
    success: bool
    total: int
    page: int
    per_page: int
    tasks: List[TaskResponse]

@app.get("/tasks", response_model=TaskListResponse)
def list_tasks(page: int = 1, per_page: int = 10):
    return {
        "success": True,
        "total": 100,
        "page": page,
        "per_page": per_page,
        "tasks": paginated_tasks
    }
```

### 8. Nested Response Models
```python
class TaskOwner(BaseModel):
    id: int
    username: str

class TaskWithOwner(BaseModel):
    id: int
    title: str
    owner: TaskOwner  # Nested!

@app.get("/tasks/{id}/with-owner", response_model=TaskWithOwner)
def get_task_with_owner(id: int):
    return {
        "id": 1,
        "title": "Task",
        "owner": {"id": 1, "username": "john"}
    }
```

---

## Response Model Options Summary

| Option | Purpose | Example |
|--------|---------|---------|
| `response_model` | Define output schema | `response_model=UserResponse` |
| `response_model_exclude_unset` | Hide None/unset fields | `=True` |
| `response_model_exclude` | Blacklist fields | `={"password", "internal_id"}` |
| `response_model_include` | Whitelist fields | `={"id", "name"}` |

---

## Multiple Models Pattern

Create different response sizes for same entity:

```python
# Minimal - for lists, dropdowns
class TaskBrief(BaseModel):
    id: int
    title: str

# Standard - normal usage
class TaskStandard(BaseModel):
    id: int
    title: str
    status: str

# Full - detailed view
class TaskFull(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str
```

---

## Test URLs

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/users | List users (no passwords) |
| http://127.0.0.1:8000/users/1 | Get user (no password) |
| http://127.0.0.1:8000/users/1/detail | User with task count |
| http://127.0.0.1:8000/tasks | List with wrapper |
| http://127.0.0.1:8000/tasks/1 | exclude_unset demo |
| http://127.0.0.1:8000/tasks/1/minimal | Excluded fields |
| http://127.0.0.1:8000/tasks/1/summary | Only included fields |
| http://127.0.0.1:8000/tasks/999/safe | Not found response |
| http://127.0.0.1:8000/tasks/1/with-owner | Nested model |
| http://127.0.0.1:8000/tasks/1/brief | Minimal response |
| http://127.0.0.1:8000/tasks/1/full | Full response |

---

## Exercises

### Exercise 1: Product API
Create models:
```python
class ProductCreate(BaseModel):
    name: str
    price: float
    cost: float  # Internal - don't expose!
    
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    # No cost field!
```

### Exercise 2: Order with Items
Create nested response:
```python
class OrderItemResponse(BaseModel):
    product_name: str
    quantity: int
    subtotal: float

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    items: List[OrderItemResponse]
    total: float
```

### Exercise 3: Paginated Response
Create wrapper:
```python
class PaginatedProducts(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool
```

### Exercise 4: Multiple Detail Levels
For `/employees` endpoint, create:
- `EmployeeBrief`: id, name
- `EmployeeStandard`: + department, title
- `EmployeeFull`: + salary, hire_date, manager

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Field missing in response | Field not in response_model | Add field to model |
| Extra fields in response | Not using response_model | Add response_model parameter |
| `None` showing in response | Field is Optional | Use `response_model_exclude_unset=True` |

---

## Best Practices

1. **Always use response_model** for endpoints returning data
2. **Never include passwords** in response models
3. **Create separate models** for input vs output
4. **Use nested models** to avoid exposing related entity secrets
5. **Use wrapper models** for lists with pagination metadata

---

## What's Next?
**Level 6: Form Data & File Uploads** - Learn to handle form submissions and file uploads with `Form()` and `File()`.
