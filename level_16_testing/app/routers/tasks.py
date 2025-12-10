"""
Tasks Router
============
CRUD endpoints for tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.database import Database, get_database
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = Query(default=None),
    priority: Optional[int] = Query(default=None, ge=1, le=5),
    db: Database = Depends(get_database)
):
    """
    List all tasks with optional filters
    
    No authentication required
    """
    tasks = db.get_all_tasks()
    
    # Apply filters
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]
    
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Database = Depends(get_database)
):
    """Get task by ID"""
    task = db.get_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Create a new task
    
    Requires authentication (X-API-Key header)
    """
    new_task = db.create_task(
        title=task.title,
        description=task.description,
        owner_id=1,  # Simplified
        priority=task.priority
    )
    
    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Update a task
    
    Requires authentication
    """
    # Check task exists
    existing = db.get_task(task_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Update
    update_data = task_update.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value
    
    updated = db.update_task(task_id, update_data)
    
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Delete a task
    
    Requires authentication
    """
    if not db.get_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    db.delete_task(task_id)


@router.get("/stats/summary")
def get_stats(db: Database = Depends(get_database)):
    """Get task statistics"""
    tasks = db.get_all_tasks()
    
    status_counts = {}
    for task in tasks:
        s = task["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    
    return {
        "total": len(tasks),
        "by_status": status_counts
    }
