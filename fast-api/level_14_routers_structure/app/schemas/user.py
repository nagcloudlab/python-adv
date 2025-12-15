"""
User Schemas
============
Pydantic models for User validation and serialization.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.user


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (no password)"""
    id: str
    role: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    total: int
    users: List[UserResponse]
