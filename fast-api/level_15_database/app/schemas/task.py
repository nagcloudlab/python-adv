"""
Task Schemas (Pydantic)
=======================
Pydantic models for Task validation and serialization.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# ============================================================
# Base Schema
# ============================================================

class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: int = Field(default=1, ge=1, le=5)
    due_date: Optional[datetime] = None


# ============================================================
# Create Schema
# ============================================================

class TaskCreate(TaskBase):
    """Schema for creating a task"""
    owner_id: int = Field(..., description="ID of the task owner")
    status: TaskStatus = TaskStatus.pending


# ============================================================
# Update Schema
# ============================================================

class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    due_date: Optional[datetime] = None


# ============================================================
# Response Schema
# ============================================================

class OwnerInTask(BaseModel):
    """Simplified owner schema for embedding in task"""
    id: int
    username: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    status: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskWithOwner(TaskResponse):
    """Task response including owner details"""
    owner: OwnerInTask
    
    model_config = ConfigDict(from_attributes=True)
