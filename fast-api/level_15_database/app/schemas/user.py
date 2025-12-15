"""
User Schemas (Pydantic)
=======================
Pydantic models for request validation and response serialization.

Note the difference:
- SQLAlchemy models (models.py) → Database structure
- Pydantic schemas (this file) → API validation/serialization
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============================================================
# Base Schema (shared fields)
# ============================================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(default=None, max_length=100)


# ============================================================
# Create Schema (for POST requests)
# ============================================================

class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


# ============================================================
# Update Schema (for PUT/PATCH requests)
# ============================================================

class UserUpdate(BaseModel):
    """Schema for updating a user (all fields optional)"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None


# ============================================================
# Response Schema (for GET responses)
# ============================================================

class UserResponse(UserBase):
    """
    Schema for user response
    
    ConfigDict with from_attributes=True allows creating
    this schema from SQLAlchemy model instances.
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Response with Tasks (for nested response)
# ============================================================

class TaskInUser(BaseModel):
    """Simplified task schema for embedding in user response"""
    id: int
    title: str
    status: str
    priority: int
    
    model_config = ConfigDict(from_attributes=True)


class UserWithTasks(UserResponse):
    """User response including their tasks"""
    tasks: List[TaskInUser] = []
    
    model_config = ConfigDict(from_attributes=True)
