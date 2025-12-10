"""
Admin Router
============
Admin-only endpoints.

This router is mounted at /admin in main.py
All endpoints require admin role.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse
from app.models.database import users_db, tasks_db
from app.core.dependencies import require_admin

# Create router with default dependency
# All endpoints in this router require admin
router = APIRouter(
    dependencies=[Depends(require_admin)]
)


# ============================================================
# Admin Endpoints
# ============================================================

@router.get("/dashboard")
def admin_dashboard():
    """
    Admin dashboard with statistics
    
    Requires admin role (X-User-Id: admin)
    """
    active_users = sum(1 for u in users_db.values() if u.get("is_active", True))
    
    tasks_by_status = {}
    for task in tasks_db.values():
        status = task["status"]
        tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
    
    return {
        "stats": {
            "total_users": len(users_db),
            "active_users": active_users,
            "total_tasks": len(tasks_db),
            "tasks_by_status": tasks_by_status
        }
    }


@router.get("/users", response_model=List[UserResponse])
def list_all_users():
    """
    List all users (admin only)
    """
    return list(users_db.values())


@router.put("/users/{user_id}/activate")
def activate_user(user_id: str):
    """
    Activate a user account
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    users_db[user_id]["is_active"] = True
    return {"message": f"User {user_id} activated"}


@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: str):
    """
    Deactivate a user account
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    users_db[user_id]["is_active"] = False
    return {"message": f"User {user_id} deactivated"}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    """
    Delete a user (admin only)
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    if user_id == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )
    
    del users_db[user_id]


@router.get("/tasks", response_model=List[TaskResponse])
def list_all_tasks():
    """
    List all tasks (admin only)
    """
    return list(tasks_db.values())


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def force_delete_task(task_id: int):
    """
    Force delete any task (admin only)
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    del tasks_db[task_id]
