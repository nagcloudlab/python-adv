"""
Pydantic Schemas
================
Request and response models.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskCreate(BaseModel):
    """Schema for creating a task"""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: int = Field(default=1, ge=1, le=5)


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    owner_id: int
    created_at: str
