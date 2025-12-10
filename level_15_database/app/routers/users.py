"""
Users Router with Database Operations
=====================================
CRUD operations for users using SQLAlchemy.

Key Concepts:
1. Dependency injection for database session
2. SQLAlchemy query methods
3. Creating, reading, updating, deleting records
4. Handling relationships
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserWithTasks

router = APIRouter()


# ============================================================
# CREATE - POST /users
# ============================================================

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user
    
    SQLAlchemy operations:
    1. Query to check if username/email exists
    2. Create new User instance
    3. Add to session
    4. Commit transaction
    5. Refresh to get generated values (id, created_at)
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    
    # Add to session and commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh to get id and created_at
    
    return db_user


# ============================================================
# READ - GET /users
# ============================================================

@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all users with pagination
    
    SQLAlchemy operations:
    - query(Model) - Start a query
    - offset(n) - Skip n records
    - limit(n) - Return max n records
    - all() - Execute and return list
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user by ID
    
    SQLAlchemy operations:
    - filter() - Add WHERE clause
    - first() - Return first result or None
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user


@router.get("/{user_id}/with-tasks", response_model=UserWithTasks)
def get_user_with_tasks(user_id: int, db: Session = Depends(get_db)):
    """
    Get user with their tasks
    
    The relationship automatically loads tasks
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user


# ============================================================
# UPDATE - PUT /users/{id}
# ============================================================

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a user
    
    SQLAlchemy operations:
    1. Query and get the record
    2. Update attributes
    3. Commit changes
    4. Refresh to get updated values
    """
    # Get user
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    # Update fields (only if provided)
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # Commit and refresh
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ============================================================
# DELETE - DELETE /users/{id}
# ============================================================

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user
    
    SQLAlchemy operations:
    1. Query and get the record
    2. Delete from session
    3. Commit transaction
    
    Note: Due to cascade="all, delete-orphan" on the relationship,
    all user's tasks will also be deleted.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    db.delete(db_user)
    db.commit()


# ============================================================
# Additional Query Examples
# ============================================================

@router.get("/search/", response_model=List[UserResponse])
def search_users(
    q: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """
    Search users with filters
    
    Demonstrates building dynamic queries
    """
    query = db.query(User)
    
    if q:
        # LIKE query for username or email
        query = query.filter(
            (User.username.ilike(f"%{q}%")) | 
            (User.email.ilike(f"%{q}%"))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.all()


@router.get("/by-username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Get user by username"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    return user
