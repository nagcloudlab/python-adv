"""
SQLAlchemy ORM Models
=====================
Database models define the structure of our database tables.

Concepts:
1. Column types (Integer, String, Boolean, DateTime, etc.)
2. Primary keys and auto-increment
3. Foreign keys for relationships
4. Relationship() for ORM navigation
5. Default values and server defaults
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# ============================================================
# CONCEPT 1: Enum for Task Status
# ============================================================

class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# ============================================================
# CONCEPT 2: User Model
# ============================================================

class User(Base):
    """
    User model - represents the 'users' table
    
    Attributes:
        id: Primary key (auto-increment)
        username: Unique username
        email: Unique email
        full_name: Optional full name
        is_active: Whether user is active
        created_at: Timestamp of creation
        tasks: Relationship to Task model (one-to-many)
    """
    
    # Table name in database
    __tablename__ = "users"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship: One user has many tasks
    # back_populates creates a bidirectional relationship
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# ============================================================
# CONCEPT 3: Task Model with Foreign Key
# ============================================================

class Task(Base):
    """
    Task model - represents the 'tasks' table
    
    Has a foreign key relationship to User (many-to-one)
    """
    
    __tablename__ = "tasks"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=TaskStatus.pending.value)
    priority = Column(Integer, default=1)
    
    # Foreign key: Each task belongs to one user
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship: Many tasks belong to one user
    owner = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


# ============================================================
# Model Relationship Summary
# ============================================================
"""
User (1) ----< (Many) Task

One User can have many Tasks
Each Task belongs to one User

In User model:
    tasks = relationship("Task", back_populates="owner")

In Task model:
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")

Usage:
    user.tasks          # Get all tasks for user
    task.owner          # Get owner of task
    task.owner.username # Get owner's username
"""
