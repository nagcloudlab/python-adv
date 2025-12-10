"""
Tasks Router
============
All task-related endpoints.

This router is mounted at /tasks in main.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.models.database import tasks_db, get_next_task_id
from app.core.dependencies import (
    Pagination,
    CommonQueryParams,
    get_current_active_user
)

# Create router
router = APIRouter()


# ============================================================
# Task Endpoints
# ============================================================

@router.get("", response_model=TaskListResponse)
def list_tasks(
    pagination: Pagination = Depends(),
    common: CommonQueryParams = Depends(),
    current_user: dict = Depends(get_current_active_user)
):
    """
    List all tasks with pagination and filtering
    
    - Requires authentication (X-User-Id header)
    - Supports pagination (page, size)
    - Supports search (q)
    - Supports sorting (sort_by, sort_order)
    """
    # Get all tasks
    tasks = list(tasks_db.values())
    
    # Filter by search query
    if common.q:
        tasks = [t for t in tasks if common.q.lower() in t["title"].lower()]
    
    # Sort
    if common.sort_by and common.sort_by in ["title", "priority", "status"]:
        reverse = common.sort_order == "desc"
        tasks = sorted(tasks, key=lambda x: x.get(common.sort_by, ""), reverse=reverse)
    
    # Get total before pagination
    total = len(tasks)
    
    # Apply pagination
    tasks = tasks[pagination.skip:pagination.skip + pagination.limit]
    
    return TaskListResponse(
        total=total,
        page=pagination.page,
        size=pagination.size,
        tasks=tasks
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a specific task by ID
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return tasks_db[task_id]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new task
    """
    task_id = get_next_task_id()
    now = datetime.now().isoformat()
    
    new_task = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority,
        "owner_id": current_user["id"],
        "created_at": now,
        "updated_at": now
    }
    
    tasks_db[task_id] = new_task
    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update an existing task
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    task = tasks_db[task_id]
    
    # Check ownership (unless admin)
    if task["owner_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )
    
    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "status":
                task[field] = value.value
            else:
                task[field] = value
    
    task["updated_at"] = datetime.now().isoformat()
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a task
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    task = tasks_db[task_id]
    
    # Check ownership (unless admin)
    if task["owner_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )
    
    del tasks_db[task_id]


@router.get("/my/tasks", response_model=List[TaskResponse])
def get_my_tasks(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get tasks owned by current user
    """
    my_tasks = [
        t for t in tasks_db.values()
        if t["owner_id"] == current_user["id"]
    ]
    return my_tasks
