"""
Users Router
============
All user-related endpoints.

This router is mounted at /users in main.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.database import users_db
from app.core.dependencies import get_current_active_user

# Create router
router = APIRouter()


# ============================================================
# User Endpoints
# ============================================================

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get current user's profile
    
    Requires X-User-Id header
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update current user's profile
    """
    user = users_db[current_user["id"]]
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            user[field] = value
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a user by ID
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return users_db[user_id]


@router.get("", response_model=List[UserResponse])
def list_users(
    current_user: dict = Depends(get_current_active_user)
):
    """
    List all users
    """
    return list(users_db.values())
