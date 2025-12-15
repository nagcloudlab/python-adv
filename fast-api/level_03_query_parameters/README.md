# Level 3: Query Parameters

## Learning Objectives
- Understand query parameters (`?key=value`)
- Create required vs optional parameters
- Set default values
- Handle multiple data types (int, bool, float)
- Accept list parameters (`?tag=a&tag=b`)
- Combine path and query parameters

---

## Setup Instructions

```bash
cd level_03_query_parameters
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Key Concepts

### 1. Query Parameters with Defaults (Optional)
```python
@app.get("/tasks")
def list_tasks(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

| URL | skip | limit |
|-----|------|-------|
| `/tasks` | 0 | 10 |
| `/tasks?limit=5` | 0 | 5 |
| `/tasks?skip=2&limit=5` | 2 | 5 |

### 2. Optional Parameters (Can be None)
```python
from typing import Optional

@app.get("/tasks/filter")
def filter_tasks(status: Optional[str] = None):
    if status:
        # Filter by status
    return tasks
```

### 3. Required Parameters (No Default)
```python
@app.get("/search")
def search(q: str):  # No default = REQUIRED
    return {"query": q}
```

| URL | Result |
|-----|--------|
| `/search?q=test` | ✅ Works |
| `/search` | ❌ 422 Error |

### 4. Boolean Parameters
```python
@app.get("/tasks/search")
def search(q: str, case_sensitive: bool = False):
    return {"case_sensitive": case_sensitive}
```

**Accepted boolean values:**
| True | False |
|------|-------|
| `true` | `false` |
| `1` | `0` |
| `yes` | `no` |
| `on` | `off` |

### 5. List Parameters
```python
from typing import List

@app.get("/tasks/by-tags")
def filter_by_tags(tag: List[str] = []):
    return {"tags": tag}
```

| URL | tag value |
|-----|-----------|
| `/tasks/by-tags?tag=python` | `["python"]` |
| `/tasks/by-tags?tag=python&tag=api` | `["python", "api"]` |

### 6. Combining Path and Query Parameters
```python
@app.get("/users/{username}/tasks")
def get_user_tasks(
    username: str,           # Path parameter
    status: Optional[str] = None,  # Query parameter
    limit: int = 10          # Query parameter
):
    return {"username": username, "status": status}
```

URL: `/users/john/tasks?status=pending&limit=5`

---

## Path vs Query Parameters

| Aspect | Path Parameter | Query Parameter |
|--------|----------------|-----------------|
| Syntax | `/tasks/{id}` | `/tasks?id=1` |
| Purpose | Identify resource | Filter/modify |
| Required | Usually yes | Can be optional |
| Example | `/users/john` | `/users?name=john` |

### When to Use Which?

**Path Parameters** - Resource identification:
- `/tasks/123` - Get task #123
- `/users/john` - Get user john

**Query Parameters** - Filtering, sorting, pagination:
- `/tasks?status=pending` - Filter tasks
- `/tasks?skip=0&limit=10` - Pagination
- `/tasks?sort=date` - Sorting

---

## Test URLs

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/tasks | Default pagination |
| http://127.0.0.1:8000/tasks?skip=2&limit=3 | Custom pagination |
| http://127.0.0.1:8000/tasks/filter?status=pending | Filter by status |
| http://127.0.0.1:8000/search?q=API | Required parameter |
| http://127.0.0.1:8000/search | Missing required (error) |
| http://127.0.0.1:8000/tasks/advanced?status=pending&priority=1&sort_by_priority=true | Multiple filters |
| http://127.0.0.1:8000/tasks/search?q=test&case_sensitive=true | Boolean parameter |
| http://127.0.0.1:8000/tasks/by-tags?tag=python&tag=api | List parameter |
| http://127.0.0.1:8000/users/john/tasks?status=completed | Path + Query |

---

## Type Conversion Table

| Python Type | Query Example | Converted Value |
|-------------|---------------|-----------------|
| `int` | `?count=5` | `5` |
| `float` | `?price=9.99` | `9.99` |
| `bool` | `?active=true` | `True` |
| `str` | `?name=john` | `"john"` |
| `List[str]` | `?tag=a&tag=b` | `["a", "b"]` |
| `Optional[str]` | (not provided) | `None` |

---

## Exercises

### Exercise 1: Pagination
Create `/products` endpoint with:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)

### Exercise 2: Multi-Filter
Create `/orders` endpoint with:
- `status`: Optional filter
- `customer_id`: Optional filter  
- `min_amount`: Optional minimum amount (float)
- `max_amount`: Optional maximum amount (float)

### Exercise 3: Search with Options
Create `/products/search` with:
- `q`: Required search term
- `category`: Optional category filter
- `in_stock`: Boolean, default True
- `sort_by`: Optional, values: "price", "name", "date"

### Exercise 4: List Parameter
Create `/reports/generate` with:
- `columns`: List of column names to include
- `format`: Output format (default: "json")

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `422 Unprocessable Entity` | Missing required param | Add the parameter |
| `422 - value is not a valid integer` | Wrong type | Pass correct type |
| Empty list for List param | Parameter not passed | Use `?tag=a&tag=b` format |

---

## What's Next?
**Level 4: Request Body (Pydantic)** - Learn to accept JSON data in POST/PUT requests using Pydantic models for validation.
