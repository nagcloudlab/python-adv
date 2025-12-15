# Level 19: OpenAPI Customization

## Learning Objectives
- Customize API metadata
- Add tag descriptions
- Write rich endpoint documentation
- Provide request/response examples
- Deprecate endpoints properly
- Hide internal endpoints
- Document multiple response types
- Customize OpenAPI schema

---

## Setup Instructions

```bash
cd level_19_openapi
pip install -r requirements.txt
uvicorn main:app --reload
```

**View Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## Key Concepts

### 1. App Metadata
```python
app = FastAPI(
    title="My API",
    description="API description with **markdown** support",
    version="1.0.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)
```

### 2. Documentation URLs
```python
app = FastAPI(
    docs_url="/docs",           # Swagger UI (None to disable)
    redoc_url="/redoc",         # ReDoc (None to disable)
    openapi_url="/openapi.json" # OpenAPI schema
)
```

### 3. Tags with Metadata
```python
tags_metadata = [
    {
        "name": "Users",
        "description": "User management operations",
        "externalDocs": {
            "description": "More info",
            "url": "https://example.com/docs/users"
        }
    },
    {
        "name": "Tasks",
        "description": "Task CRUD operations"
    }
]

app = FastAPI(openapi_tags=tags_metadata)
```

### 4. Operation Documentation
```python
@app.get(
    "/items",
    tags=["Items"],
    summary="List all items",
    description="Retrieve items with **markdown** support",
    response_description="List of items",
    deprecated=False
)
def list_items():
    """
    Docstring also appears in documentation.
    
    Supports **markdown** formatting.
    """
    return []
```

### 5. Field Examples (Pydantic)
```python
class Task(BaseModel):
    title: str = Field(
        ...,
        description="Task title",
        json_schema_extra={"example": "Buy groceries"}
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=5,
        json_schema_extra={"example": 3}
    )
```

### 6. Model Examples
```python
class TaskCreate(BaseModel):
    title: str
    priority: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Complete project",
                "priority": 5
            }
        }
    }
```

### 7. Multiple Examples (Body)
```python
@app.post("/tasks")
def create_task(
    task: TaskCreate = Body(
        ...,
        openapi_examples={
            "simple": {
                "summary": "Simple task",
                "value": {"title": "Buy milk"}
            },
            "detailed": {
                "summary": "Detailed task",
                "value": {
                    "title": "Project proposal",
                    "priority": 5
                }
            }
        }
    )
):
    pass
```

### 8. Response Documentation
```python
@app.get(
    "/tasks/{id}",
    responses={
        200: {
            "description": "Task found",
            "model": TaskResponse
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"error": "Not found"}
                }
            }
        }
    }
)
def get_task(id: int):
    pass
```

### 9. Deprecated Endpoints
```python
@app.get(
    "/old-endpoint",
    deprecated=True,
    summary="[DEPRECATED] Old endpoint"
)
def old_endpoint():
    """Deprecated: Use /new-endpoint instead."""
    pass
```

### 10. Hidden Endpoints
```python
@app.get(
    "/internal/debug",
    include_in_schema=False  # Not in OpenAPI docs
)
def debug():
    return {"debug": True}
```

### 11. Custom OpenAPI Schema
```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes
    )
    
    # Add custom fields
    schema["info"]["x-logo"] = {"url": "https://..."}
    
    # Add security schemes
    schema["components"]["securitySchemes"] = {
        "ApiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    }
    
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
```

---

## Documentation Best Practices

### Good Summary
```python
summary="Create a new task"  # ✅ Concise
summary="This endpoint creates a new task in the database"  # ❌ Too long
```

### Good Description
```python
description="""
Create a new task.

### Required Fields
- **title**: Task title

### Optional Fields  
- **priority**: 1-5 (default: 1)

### Returns
Created task with ID.
"""
```

### Good Examples
```python
# Realistic data
{"title": "Complete Q2 report", "priority": 4}  # ✅

# Placeholder data
{"title": "string", "priority": 0}  # ❌
```

---

## Swagger UI vs ReDoc

| Feature | Swagger UI | ReDoc |
|---------|------------|-------|
| Try it out | ✅ Yes | ❌ No |
| Search | ❌ No | ✅ Yes |
| Three-panel | ❌ No | ✅ Yes |
| Customizable | Limited | Extensive |
| Best for | Testing | Reading |

---

## Servers Configuration

```python
app = FastAPI(
    servers=[
        {"url": "http://localhost:8000", "description": "Development"},
        {"url": "https://api.example.com", "description": "Production"},
        {"url": "https://staging.example.com", "description": "Staging"}
    ]
)
```

---

## Security Schemes

```python
# In custom_openapi():
schema["components"]["securitySchemes"] = {
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
    },
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    },
    "OAuth2": {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": "/token",
                "scopes": {
                    "read": "Read access",
                    "write": "Write access"
                }
            }
        }
    }
}
```

---

## Exercises

### Exercise 1: Complete Documentation
Add rich documentation to all endpoints:
- Summary and description
- Request/response examples
- Error responses

### Exercise 2: API Versioning
- Add version prefix `/v1/`
- Document breaking changes
- Show migration path

### Exercise 3: Custom Theme
- Customize Swagger UI colors
- Add company logo
- Custom favicon

### Exercise 4: SDK Generation
- Export OpenAPI JSON
- Generate client SDK using openapi-generator
- Test generated client

---

## Common Patterns

### Pagination Documentation
```python
@app.get("/items")
def list_items(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Returns paginated results.
    
    Response includes:
    - `items`: List of items
    - `total`: Total count
    - `page`: Current page
    - `pages`: Total pages
    """
    pass
```

### Error Response Model
```python
class ErrorResponse(BaseModel):
    code: str = Field(..., example="VALIDATION_ERROR")
    message: str = Field(..., example="Invalid input")
    details: Optional[dict] = None
    
@app.get(
    "/items/{id}",
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        422: {"model": ErrorResponse, "description": "Validation error"}
    }
)
def get_item(id: int):
    pass
```

---

## Best Practices

1. **Write clear summaries** - One line, action-focused
2. **Use markdown** - Format descriptions nicely
3. **Provide realistic examples** - Not placeholder data
4. **Document all responses** - Including errors
5. **Group with tags** - Organize related endpoints
6. **Deprecate properly** - Before removing endpoints
7. **Hide internal endpoints** - Don't expose debug routes

---

## What's Next?
**Level 20: Deployment** - Deploy FastAPI with Docker, Gunicorn, and production configurations.
