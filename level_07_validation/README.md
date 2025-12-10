# Level 7: Advanced Validation

## Learning Objectives
- Use `Path()` to validate path parameters
- Use `Query()` to validate query parameters
- Use `Field()` to validate Pydantic model fields
- Use `Body()` for body parameter validation
- Apply numeric constraints (ge, le, gt, lt)
- Apply string constraints (min_length, max_length, pattern)
- Write custom validators with `@field_validator`
- Write cross-field validators with `@model_validator`
- Use `Annotated` type hints (modern approach)

---

## Setup Instructions

```bash
cd level_07_validation
pip install -r requirements.txt
uvicorn main:app --reload
```

**Tip:** Check Swagger UI at `/docs` - it displays all validation constraints!

---

## ⚠️ Important: Annotated Syntax

When using `Annotated` with `Query`/`Path`/`Body`, the **default value must be set with `=` AFTER the type**, not inside the validator:

```python
# ✅ CORRECT
skip: Annotated[int, Query(ge=0)] = 0

# ❌ WRONG - Will cause AssertionError!
skip: Annotated[int, Query(default=0, ge=0)]
```

---

## Key Concepts

### 1. Path() Validator
```python
from fastapi import Path
from typing import Annotated

@app.get("/tasks/{task_id}")
def get_task(
    task_id: Annotated[int, Path(
        title="Task ID",
        description="The task identifier",
        ge=1,          # >= 1
        le=10000,      # <= 10000
        example=42
    )]
):
    return {"task_id": task_id}
```

### 2. Query() Validator
```python
from fastapi import Query

@app.get("/tasks")
def list_tasks(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[Optional[str], Query(
        min_length=2,
        max_length=50
    )] = None
):
    return {"skip": skip, "limit": limit}
```

### 3. Field() Validator (Pydantic)
```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(
        ...,                    # Required
        min_length=3,
        max_length=100,
        description="Task title"
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=5
    )
    estimated_hours: float = Field(
        default=1.0,
        gt=0,                   # > 0 (not equal)
        le=1000
    )
```

### 4. Regex Pattern Validation
```python
class UserCreate(BaseModel):
    # Username: lowercase letters, numbers, underscore
    username: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_]*$"
    )
    
    # Phone: 10-15 digits with optional + prefix
    phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+?[1-9]\d{9,14}$"
    )
```

### 5. Custom Field Validator
```python
from pydantic import field_validator

class AccountCreate(BaseModel):
    email: str
    password: str
    age: Optional[int] = None
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email")
        return v.lower()  # Transform value
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password too short")
        if not any(c.isupper() for c in v):
            raise ValueError("Need uppercase letter")
        return v
```

### 6. Model-Level Validator (Cross-Field)
```python
from pydantic import model_validator

class PasswordChange(BaseModel):
    new_password: str
    confirm_password: str
    
    @model_validator(mode='after')
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
```

### 7. Date Range Validation
```python
from datetime import date

class DateRange(BaseModel):
    start_date: date
    end_date: date
    
    @model_validator(mode='after')
    def validate_range(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        
        days = (self.end_date - self.start_date).days
        if days > 90:
            raise ValueError("Max range is 90 days")
        return self
```

---

## Validation Constraints Reference

### Numeric Constraints

| Constraint | Meaning | Example |
|------------|---------|---------|
| `gt` | Greater than | `gt=0` → must be > 0 |
| `ge` | Greater than or equal | `ge=1` → must be >= 1 |
| `lt` | Less than | `lt=100` → must be < 100 |
| `le` | Less than or equal | `le=100` → must be <= 100 |

### String Constraints

| Constraint | Meaning | Example |
|------------|---------|---------|
| `min_length` | Minimum length | `min_length=3` |
| `max_length` | Maximum length | `max_length=100` |
| `pattern` | Regex pattern | `pattern=r"^[a-z]+$"` |

### List Constraints

| Constraint | Meaning | Example |
|------------|---------|---------|
| `min_length` | Minimum items | `min_length=1` |
| `max_length` | Maximum items | `max_length=10` |

---

## Common Regex Patterns

| Purpose | Pattern | Examples |
|---------|---------|----------|
| Username | `^[a-z][a-z0-9_]*$` | john_doe, user123 |
| Email | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` | user@example.com |
| Phone | `^\+?[1-9]\d{9,14}$` | +919876543210 |
| Date | `^\d{4}-\d{2}-\d{2}$` | 2024-01-15 |
| Order ID | `^ORD-[0-9]{6}$` | ORD-123456 |
| Discount Code | `^[A-Z]{3,10}[0-9]{2,4}$` | SAVE20, DISCOUNT100 |
| UUID | `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$` | UUID format |
| Alphanumeric | `^[a-zA-Z0-9]+$` | ABC123 |
| Slug | `^[a-z0-9]+(?:-[a-z0-9]+)*$` | my-blog-post |

---

## Annotated vs Old Style

### Modern (Recommended)
```python
from typing import Annotated

@app.get("/tasks/{task_id}")
def get_task(
    task_id: Annotated[int, Path(ge=1)]
):
    pass
```

### Old Style (Still Works)
```python
@app.get("/tasks/{task_id}")
def get_task(
    task_id: int = Path(..., ge=1)
):
    pass
```

---

## Test URLs

| URL | Test |
|-----|------|
| `/tasks/0` | Path validation fail (ge=1) |
| `/tasks/1` | Path validation pass |
| `/users/AB` | Pattern fail (too short) |
| `/users/john_doe` | Pattern pass |
| `/tasks?limit=200` | Query fail (le=100) |
| `/tasks?limit=50` | Query pass |

### POST Test Bodies

**Valid Task:**
```json
{"title": "Valid Task", "priority": 3}
```

**Invalid Task (title too short):**
```json
{"title": "AB", "priority": 3}
```

**Valid Password Change:**
```json
{
    "current_password": "OldPass123",
    "new_password": "NewPass456",
    "confirm_password": "NewPass456"
}
```

**Invalid (passwords don't match):**
```json
{
    "current_password": "OldPass123",
    "new_password": "NewPass456",
    "confirm_password": "DifferentPass"
}
```

---

## Exercises

### Exercise 1: Product Validation
Create `ProductCreate` model with:
- `sku`: Pattern `^[A-Z]{2}-[0-9]{4}$` (e.g., AB-1234)
- `name`: 2-100 characters
- `price`: > 0, <= 99999.99
- `quantity`: >= 0, <= 10000

### Exercise 2: User Registration
Create registration with validators:
- `username`: 3-20 chars, alphanumeric + underscore
- `email`: Valid email format
- `password`: Min 8 chars, must have uppercase, lowercase, digit
- `confirm_password`: Must match password
- `birth_date`: Must be at least 13 years old

### Exercise 3: Booking System
Create `BookingCreate` with:
- `check_in`: date
- `check_out`: date (must be after check_in)
- `guests`: 1-10
- `room_type`: Enum (standard, deluxe, suite)
- Validate: max stay 30 days

### Exercise 4: API Key Validation
Create endpoint with:
- Path: `/api/{version}/data`
- `version`: Pattern `^v[0-9]+$` (v1, v2, etc.)
- Header: `X-API-Key` with pattern `^[A-Za-z0-9]{32}$`

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `value is not a valid integer` | Wrong type | Pass correct type |
| `ensure this value is >= 1` | Failed ge constraint | Pass value >= 1 |
| `string does not match regex` | Pattern mismatch | Follow regex pattern |
| `Value error, ...` | Custom validator failed | Fix based on message |

---

## Best Practices

1. **Always validate** user input at API boundary
2. **Use Field()** for all model fields with constraints
3. **Prefer Annotated** syntax for modern code
4. **Write custom validators** for complex business rules
5. **Use model_validator** for cross-field validation
6. **Document constraints** in descriptions
7. **Provide examples** in schema for Swagger UI

---

## What's Next?
**Level 8: Headers & Cookies** - Learn to read/set HTTP headers, handle cookies, and work with request metadata.
