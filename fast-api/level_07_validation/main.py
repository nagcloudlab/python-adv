"""
Level 7: Advanced Validation
============================
Concepts Covered:
    - Path() validator for path parameters
    - Query() validator for query parameters
    - Field() validator for Pydantic model fields
    - Body() validator for body parameters
    - Numeric constraints (ge, le, gt, lt)
    - String constraints (min_length, max_length, pattern)
    - Regex patterns for validation
    - Custom validators with @field_validator
    - Model-level validators with @model_validator
    - Annotated type hints (modern approach)

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs (Swagger UI shows all constraints)

IMPORTANT NOTE:
    When using Annotated with Query/Path/Body, the default value
    must be set with = AFTER the type, NOT inside Query().
    
    ✅ Correct: param: Annotated[int, Query(ge=0)] = 0
    ❌ Wrong:   param: Annotated[int, Query(default=0, ge=0)]
"""

from fastapi import FastAPI, Path, Query, Body, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
from typing import Optional, List, Annotated
from datetime import date, datetime
from enum import Enum
import re

app = FastAPI(
    title="Task Manager API - Level 7",
    description="Learning Advanced Validation",
    version="7.0.0"
)


# ============================================================
# CONCEPT 1: Path() Validator
# ============================================================
# Validate and document path parameters

@app.get("/tasks/{task_id}")
def get_task(
    task_id: Annotated[int, Path(
        title="Task ID",
        description="The unique identifier of the task",
        ge=1,           # greater than or equal to 1
        le=10000,       # less than or equal to 10000
        example=42
    )]
):
    """
    Get task by ID with validation
    
    Path constraints:
    - task_id must be >= 1
    - task_id must be <= 10000
    
    Try: /tasks/0 or /tasks/99999 to see validation errors
    """
    return {"task_id": task_id, "title": f"Task {task_id}"}


@app.get("/users/{username}")
def get_user(
    username: Annotated[str, Path(
        title="Username",
        description="User's unique username",
        min_length=3,
        max_length=20,
        pattern=r"^[a-z0-9_]+$",  # lowercase, numbers, underscore only
        example="john_doe"
    )]
):
    """
    Get user by username with pattern validation
    
    Username rules:
    - 3-20 characters
    - Only lowercase letters, numbers, underscore
    - Regex: ^[a-z0-9_]+$
    
    Valid: john_doe, user123, admin_01
    Invalid: John, user@name, ab
    """
    return {"username": username, "message": f"Hello, {username}!"}


# ============================================================
# CONCEPT 2: Query() Validator
# ============================================================
# IMPORTANT: When using Annotated, default value goes with = AFTER the type
# NOT inside Query()

@app.get("/tasks")
def list_tasks(
    skip: Annotated[int, Query(
        ge=0,
        description="Number of records to skip"
    )] = 0,  # ✅ Default value HERE, not in Query()
    limit: Annotated[int, Query(
        ge=1,
        le=100,
        description="Max records to return (1-100)"
    )] = 10,  # ✅ Default value HERE
    search: Annotated[Optional[str], Query(
        min_length=2,
        max_length=50,
        description="Search term (2-50 characters)"
    )] = None,  # ✅ Default value HERE
    priority: Annotated[Optional[int], Query(
        ge=1,
        le=5,
        description="Filter by priority (1-5)"
    )] = None  # ✅ Default value HERE
):
    """
    List tasks with validated query parameters
    
    Constraints:
    - skip: >= 0
    - limit: 1-100
    - search: 2-50 characters (if provided)
    - priority: 1-5 (if provided)
    """
    return {
        "skip": skip,
        "limit": limit,
        "search": search,
        "priority": priority
    }


# Query with regex pattern
@app.get("/orders")
def list_orders(
    order_id: Annotated[Optional[str], Query(
        pattern=r"^ORD-[0-9]{6}$",
        description="Order ID format: ORD-XXXXXX"
    )] = None,
    date_from: Annotated[Optional[str], Query(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date format: YYYY-MM-DD"
    )] = None
):
    """
    List orders with pattern validation
    
    order_id format: ORD-123456
    date_from format: 2024-01-15
    """
    return {
        "order_id": order_id,
        "date_from": date_from
    }


# Query list with validation
@app.get("/tasks/filter")
def filter_tasks(
    tags: Annotated[List[str], Query(
        description="Filter by tags"
    )] = []
):
    """
    Filter tasks by multiple tags
    
    Example: /tasks/filter?tags=urgent&tags=backend
    """
    return {"tags": tags, "count": len(tags)}


# Deprecated query parameter
@app.get("/search")
def search(
    q: Annotated[Optional[str], Query(
        deprecated=True,
        description="DEPRECATED: Use 'query' instead"
    )] = None,
    query: Annotated[Optional[str], Query(
        min_length=1,
        description="Search query"
    )] = None
):
    """
    Search endpoint with deprecated parameter
    
    'q' is deprecated, use 'query' instead
    Swagger UI will show 'q' as deprecated
    """
    search_term = query or q
    return {"search_term": search_term}


# ============================================================
# CONCEPT 3: Field() Validator in Pydantic Models
# ============================================================

class TaskCreate(BaseModel):
    """Task creation with Field validation"""
    
    title: str = Field(
        ...,  # Required
        min_length=3,
        max_length=100,
        description="Task title (3-100 characters)",
        examples=["Complete project report"]
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Task description (max 500 characters)"
    )
    
    priority: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Priority level (1=lowest, 5=highest)"
    )
    
    estimated_hours: float = Field(
        default=1.0,
        gt=0,         # greater than 0
        le=1000,      # max 1000 hours
        description="Estimated hours to complete"
    )
    
    tags: List[str] = Field(
        default=[],
        max_length=10,  # Max 10 tags
        description="Tags (max 10)"
    )


@app.post("/tasks")
def create_task(task: TaskCreate):
    """Create task with validated fields"""
    return {"message": "Task created", "task": task.model_dump()}


# ============================================================
# CONCEPT 4: Regex Pattern Validation
# ============================================================

class UserCreate(BaseModel):
    """User creation with regex patterns"""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-z][a-z0-9_]*$",  # Start with letter
        description="Username: start with letter, then letters/numbers/underscore"
    )
    
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    
    phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+?[1-9]\d{9,14}$",
        description="Phone: 10-15 digits, optional + prefix"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Password (8-50 characters)"
    )


@app.post("/users")
def create_user(user: UserCreate):
    """Create user with pattern validation"""
    return {
        "message": "User created",
        "username": user.username,
        "email": user.email
    }


# ============================================================
# CONCEPT 5: Custom Field Validators (@field_validator)
# ============================================================

class AccountCreate(BaseModel):
    """Account with custom validators"""
    
    username: str = Field(..., min_length=3)
    email: str
    password: str = Field(..., min_length=8)
    confirm_password: str
    age: Optional[int] = None
    website: Optional[str] = None
    
    # Validate single field
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Custom email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()  # Normalize to lowercase
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Username must be alphanumeric"""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscore allowed)")
        if v[0].isdigit():
            raise ValueError("Username cannot start with a number")
        return v.lower()
    
    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        """Age must be reasonable"""
        if v is not None:
            if v < 13:
                raise ValueError("Must be at least 13 years old")
            if v > 120:
                raise ValueError("Invalid age")
        return v
    
    @field_validator("website")
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        """Website must be valid URL"""
        if v is not None:
            if not v.startswith(("http://", "https://")):
                raise ValueError("Website must start with http:// or https://")
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Password strength validation"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


@app.post("/accounts")
def create_account(account: AccountCreate):
    """Create account with custom validation"""
    return {
        "message": "Account created",
        "username": account.username,
        "email": account.email
    }


# ============================================================
# CONCEPT 6: Model-Level Validators (@model_validator)
# ============================================================

class PasswordChange(BaseModel):
    """Password change with cross-field validation"""
    
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @model_validator(mode='after')
    def validate_passwords(self):
        """Validate password fields together"""
        # Check passwords match
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirm password do not match")
        
        # Check new password is different from current
        if self.new_password == self.current_password:
            raise ValueError("New password must be different from current password")
        
        return self


@app.post("/password/change")
def change_password(data: PasswordChange):
    """Change password with cross-field validation"""
    return {"message": "Password changed successfully"}


# Date range validation
class DateRange(BaseModel):
    """Date range with validation"""
    
    start_date: date
    end_date: date
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate date range"""
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        
        # Max range: 90 days
        delta = (self.end_date - self.start_date).days
        if delta > 90:
            raise ValueError("Date range cannot exceed 90 days")
        
        return self


@app.post("/reports/generate")
def generate_report(date_range: DateRange):
    """Generate report for date range"""
    days = (date_range.end_date - date_range.start_date).days
    return {
        "start_date": date_range.start_date.isoformat(),
        "end_date": date_range.end_date.isoformat(),
        "days": days
    }


# ============================================================
# CONCEPT 7: Body() Validator
# ============================================================

class Item(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


@app.post("/items")
def create_item(
    item: Item,
    importance: Annotated[int, Body(
        ge=1,
        le=10,
        description="Item importance (1-10)"
    )] = 5  # ✅ Default value HERE
):
    """
    Create item with separate body parameter
    
    Request body:
    {
        "item": {"name": "...", "price": ...},
        "importance": 5
    }
    """
    return {
        "item": item.model_dump(),
        "importance": importance
    }


# Embed body model
@app.post("/items/embedded")
def create_item_embedded(
    item: Annotated[Item, Body(embed=True)]
):
    """
    Create item with embedded body
    
    With embed=True, expects:
    {"item": {"name": "...", "price": ...}}
    
    Without embed:
    {"name": "...", "price": ...}
    """
    return {"item": item.model_dump()}


# ============================================================
# CONCEPT 8: Complex Validation Example
# ============================================================

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItem(BaseModel):
    """Order item with validation"""
    
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1, le=100)
    unit_price: float = Field(..., gt=0)
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


class OrderCreate(BaseModel):
    """Complex order with multiple validations"""
    
    customer_email: EmailStr
    shipping_address: str = Field(..., min_length=10, max_length=200)
    items: List[OrderItem] = Field(..., min_length=1, max_length=50)
    discount_code: Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{3,10}[0-9]{2,4}$",
        description="Discount code: 3-10 uppercase letters + 2-4 digits"
    )
    notes: Optional[str] = Field(default=None, max_length=500)
    
    @field_validator("items")
    @classmethod
    def validate_items(cls, v: List[OrderItem]) -> List[OrderItem]:
        """Validate items list"""
        product_ids = [item.product_id for item in v]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate products not allowed")
        return v
    
    @model_validator(mode='after')
    def validate_order(self):
        """Validate entire order"""
        total = sum(item.quantity * item.unit_price for item in self.items)
        if total < 10:
            raise ValueError("Minimum order value is $10")
        if total > 10000:
            raise ValueError("Maximum order value is $10,000")
        return self


@app.post("/orders")
def create_order(order: OrderCreate):
    """Create order with comprehensive validation"""
    total = sum(item.quantity * item.unit_price for item in order.items)
    return {
        "message": "Order created",
        "customer_email": order.customer_email,
        "item_count": len(order.items),
        "total": round(total, 2),
        "discount_code": order.discount_code
    }


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 7 - Advanced Validation",
        "important_note": "When using Annotated, set default with = AFTER type, not inside Query()",
        "concepts": [
            "Path() - path parameter validation",
            "Query() - query parameter validation",
            "Field() - Pydantic field validation",
            "Body() - body parameter validation",
            "@field_validator - custom field validation",
            "@model_validator - cross-field validation"
        ],
        "test_endpoints": [
            "GET /tasks/{task_id} - Path validation",
            "GET /users/{username} - Pattern validation",
            "GET /tasks - Query validation",
            "POST /tasks - Field validation",
            "POST /users - Regex patterns",
            "POST /accounts - Custom validators",
            "POST /password/change - Model validator",
            "POST /reports/generate - Date range",
            "POST /orders - Complex validation"
        ]
    }
