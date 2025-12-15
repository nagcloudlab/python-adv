# Level 9: Status Codes & Exception Handling

## Learning Objectives
- Understand HTTP status codes and when to use them
- Set explicit status codes on endpoints
- Use `HTTPException` for error responses
- Create custom exception classes
- Write exception handlers with `@app.exception_handler`
- Handle validation errors (`RequestValidationError`)
- Implement generic error handling
- Document error responses in OpenAPI

---

## Setup Instructions

```bash
cd level_09_status_exceptions
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## HTTP Status Codes Overview

### Success (2xx)
| Code | Name | Usage |
|------|------|-------|
| 200 | OK | Standard success (GET, PUT, PATCH) |
| 201 | Created | Resource created (POST) |
| 202 | Accepted | Request accepted, processing async |
| 204 | No Content | Success, no body (DELETE) |

### Client Errors (4xx)
| Code | Name | Usage |
|------|------|-------|
| 400 | Bad Request | Invalid request syntax |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (duplicate) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |

### Server Errors (5xx)
| Code | Name | Usage |
|------|------|-------|
| 500 | Internal Server Error | Unexpected server error |
| 502 | Bad Gateway | Upstream server error |
| 503 | Service Unavailable | Service down/maintenance |

---

## Key Concepts

### 1. Setting Status Codes
```python
from fastapi import status

# 201 Created
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    return new_task

# 204 No Content (no return needed)
@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    del tasks_db[id]
```

### 2. HTTPException - Basic
```python
from fastapi import HTTPException

@app.get("/tasks/{id}")
def get_task(id: int):
    if id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    return tasks_db[id]
```

### 3. HTTPException - With Headers
```python
raise HTTPException(
    status_code=401,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"}
)
```

### 4. HTTPException - Detailed Error
```python
raise HTTPException(
    status_code=404,
    detail={
        "error_code": "TASK_NOT_FOUND",
        "message": f"Task {id} not found",
        "task_id": id,
        "timestamp": datetime.now().isoformat()
    }
)
```

### 5. Custom Exception Classes
```python
class TaskNotFoundException(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        self.message = f"Task {task_id} not found"

class PermissionDeniedException(Exception):
    def __init__(self, user: str, action: str):
        self.user = user
        self.action = action
```

### 6. Exception Handlers
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(TaskNotFoundException)
async def task_not_found_handler(request: Request, exc: TaskNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "TASK_NOT_FOUND",
            "message": exc.message,
            "task_id": exc.task_id
        }
    )
```

### 7. Validation Error Handler
```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=422,
        content={"error": "VALIDATION_ERROR", "details": errors}
    )
```

### 8. Generic Exception Handler
```python
@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    # Log error in production
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    )
```

### 9. Document Error Responses
```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    message: str

@app.get(
    "/tasks/{id}",
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
        403: {"model": ErrorResponse, "description": "Access denied"}
    }
)
def get_task(id: int):
    ...
```

---

## Status Code Constants

Use `fastapi.status` for readable code:

```python
from fastapi import status

status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_204_NO_CONTENT
status.HTTP_400_BAD_REQUEST
status.HTTP_401_UNAUTHORIZED
status.HTTP_403_FORBIDDEN
status.HTTP_404_NOT_FOUND
status.HTTP_409_CONFLICT
status.HTTP_422_UNPROCESSABLE_ENTITY
status.HTTP_429_TOO_MANY_REQUESTS
status.HTTP_500_INTERNAL_SERVER_ERROR
status.HTTP_503_SERVICE_UNAVAILABLE
```

---

## Error Response Patterns

### Pattern 1: Simple Message
```json
{
    "detail": "Task not found"
}
```

### Pattern 2: Error Code + Message
```json
{
    "error": "TASK_NOT_FOUND",
    "message": "Task with id 42 does not exist"
}
```

### Pattern 3: Detailed Error
```json
{
    "error": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
        {"field": "title", "message": "ensure this value has at least 3 characters"}
    ],
    "timestamp": "2024-01-15T10:30:00"
}
```

### Pattern 4: With Request Context
```json
{
    "error": "NOT_FOUND",
    "message": "Resource not found",
    "path": "/api/tasks/42",
    "request_id": "req-abc123",
    "timestamp": "2024-01-15T10:30:00"
}
```

---

## Test Scenarios

### Test Basic HTTPException
```bash
# 404 Not Found
curl http://localhost:8000/tasks/999

# 201 Created
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task"}'
```

### Test Custom Exceptions
```bash
# TaskNotFoundException
curl http://localhost:8000/v2/tasks/999

# PermissionDeniedException
curl -X DELETE "http://localhost:8000/v2/tasks/1?username=user1"

# RateLimitExceededException
curl http://localhost:8000/v2/limited
```

### Test Validation Error
```bash
curl -X POST http://localhost:8000/tasks/strict \
  -H "Content-Type: application/json" \
  -d '{"title": "AB", "priority": 10, "tags": []}'
```

### Test Status Codes
```bash
curl http://localhost:8000/status/200
curl http://localhost:8000/status/401
curl http://localhost:8000/status/404
curl http://localhost:8000/status/429
```

---

## Exercises

### Exercise 1: Product API Errors
Create endpoints with proper error handling:
- `GET /products/{id}` → 404 if not found
- `POST /products` → 409 if SKU exists
- `DELETE /products/{id}` → 204 on success

### Exercise 2: Custom Business Exceptions
Create and handle:
- `OutOfStockException` → 400
- `OrderLimitExceededException` → 400
- `PaymentFailedException` → 402

### Exercise 3: Comprehensive Error Response
Create an error response model with:
- error_code (string)
- message (string)
- details (optional list)
- timestamp (datetime)
- request_id (string)
- path (string)

### Exercise 4: Rate Limiter
Implement rate limiting:
- Track requests per IP
- Raise exception when limit exceeded
- Include `Retry-After` and `X-RateLimit-*` headers

---

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Using 200 for creation | Use 201 Created |
| Using 200 for deletion | Use 204 No Content |
| Using 401 for authorization | Use 403 Forbidden |
| Exposing stack traces | Use generic error handler |
| Not documenting errors | Use `responses` parameter |

---

## Best Practices

1. **Use appropriate status codes** - Don't use 200 for everything
2. **Be consistent** - Use same error format across API
3. **Don't expose internals** - Generic messages for 500 errors
4. **Include error codes** - Makes client-side handling easier
5. **Log errors server-side** - But don't expose in response
6. **Document all errors** - Use `responses` parameter
7. **Handle validation errors** - Customize for better UX
8. **Include request context** - request_id, path, timestamp

---

## What's Next?
**Level 10: Dependency Injection** - Learn to use `Depends()` for shared logic, database connections, authentication, and more.
