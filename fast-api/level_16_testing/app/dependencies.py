"""
Dependencies
============
Shared dependencies for authentication and database access.
"""

from fastapi import Header, HTTPException, Depends
from typing import Annotated, Optional
from app.database import Database, get_database


def get_api_key(
    x_api_key: Annotated[Optional[str], Header()] = None
) -> Optional[str]:
    """Extract API key from header"""
    return x_api_key


def get_current_user(
    api_key: Optional[str] = Depends(get_api_key),
    db: Database = Depends(get_database)
) -> dict:
    """
    Get current user from API key
    
    Raises 401 if no key or invalid key
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required"
        )
    
    user = db.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return user


def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user
