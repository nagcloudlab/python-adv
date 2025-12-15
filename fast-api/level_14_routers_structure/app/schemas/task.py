"""
Task Schemas
============
Pydantic models for Task validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskBase(BaseModel):
    """Base task schema with common fields"""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: int = Field(default=1, ge=1, le=5)


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    status: TaskStatus = TaskStatus.pending


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)"""
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    status: TaskStatus
    owner_id: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list"""
    total: int
    page: int
    size: int
    tasks: List[TaskResponse]
