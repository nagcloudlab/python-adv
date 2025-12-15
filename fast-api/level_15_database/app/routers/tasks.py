"""
Tasks Router with Database Operations
=====================================
CRUD operations for tasks using SQLAlchemy.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Task, User, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskWithOwner

router = APIRouter()


# ============================================================
# CREATE - POST /tasks
# ============================================================

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task
    
    Requires a valid owner_id (user must exist)
    """
    # Verify owner exists
    owner = db.query(User).filter(User.id == task.owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {task.owner_id} not found"
        )
    
    # Create task
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority,
        owner_id=task.owner_id,
        due_date=task.due_date
    )
    
    db.add(db_task) # INSERT INTO tasks ...
    db.commit()
    db.refresh(db_task)
    
    return db_task


# ============================================================
# READ - GET /tasks
# ============================================================

@router.get("", response_model=List[TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(default=None, description="Filter by status"),
    priority: Optional[int] = Query(default=None, ge=1, le=5, description="Filter by priority"),
    owner_id: Optional[int] = Query(default=None, description="Filter by owner"),
    db: Session = Depends(get_db)
):
    """
    List tasks with optional filters
    """
    query = db.query(Task) # SELECT * FROM tasks
    
    # Apply filters
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if owner_id:
        query = query.filter(Task.owner_id == owner_id)
    
    # Order by priority (descending) and created_at
    query = query.order_by(Task.priority.desc(), Task.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return task


@router.get("/{task_id}/with-owner", response_model=TaskWithOwner)
def get_task_with_owner(task_id: int, db: Session = Depends(get_db)):
    """Get task with owner details"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return task


# ============================================================
# UPDATE - PUT /tasks/{id}
# ============================================================

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "status" and value:
            setattr(db_task, field, value.value)
        else:
            setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    status: TaskStatus,
    db: Session = Depends(get_db)
):
    """Update only task status"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    db_task.status = status.value
    db.commit()
    db.refresh(db_task)
    
    return {"message": f"Task status updated to {status.value}", "task_id": task_id}


# ============================================================
# DELETE - DELETE /tasks/{id}
# ============================================================

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    db.delete(db_task)
    db.commit()


# ============================================================
# Additional Endpoints
# ============================================================

@router.get("/user/{user_id}", response_model=List[TaskResponse])
def get_tasks_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get all tasks for a specific user"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    tasks = db.query(Task).filter(Task.owner_id == user_id).all()
    return tasks


@router.get("/stats/summary")
def get_task_stats(db: Session = Depends(get_db)):
    """Get task statistics"""
    from sqlalchemy import func
    
    total = db.query(func.count(Task.id)).scalar()
    
    # Count by status
    status_counts = db.query(
        Task.status,
        func.count(Task.id)
    ).group_by(Task.status).all()
    
    # Count by priority
    priority_counts = db.query(
        Task.priority,
        func.count(Task.id)
    ).group_by(Task.priority).all()
    
    return {
        "total_tasks": total,
        "by_status": {status: count for status, count in status_counts},
        "by_priority": {priority: count for priority, count in priority_counts}
    }
