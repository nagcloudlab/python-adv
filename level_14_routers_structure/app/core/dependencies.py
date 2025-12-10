"""
Shared Dependencies
===================
Dependencies that can be used across multiple routers.
"""

from fastapi import Header, HTTPException, Query, Depends
from typing import Optional, Annotated
from app.core.config import settings
from app.models.database import users_db


# ============================================================
# Pagination Dependency
# ============================================================

class Pagination:
    """
    Reusable pagination dependency
    
    Usage:
        def list_items(pagination: Pagination = Depends()):
            return items[pagination.skip:pagination.skip + pagination.limit]
    """
    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number"),
        size: int = Query(
            default=settings.DEFAULT_PAGE_SIZE,
            ge=1,
            le=settings.MAX_PAGE_SIZE,
            description="Items per page"
        )
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


# ============================================================
# API Key Authentication
# ============================================================

def verify_api_key(
    x_api_key: Annotated[str, Header(description="API Key")]
) -> str:
    """
    Verify API key from header
    
    Usage:
        @router.get("/protected")
        def protected(api_key: str = Depends(verify_api_key)):
            return {"key": api_key}
    """
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    return x_api_key


# ============================================================
# Current User Dependency
# ============================================================

def get_current_user(
    x_user_id: Annotated[Optional[str], Header(default=None)] = None
) -> dict:
    """
    Get current user from header (simplified auth)
    
    In real app, this would decode JWT token
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID header required"
        )
    
    if x_user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return users_db[x_user_id]


def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current active user
    
    Chains with get_current_user
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=403,
            detail="User is inactive"
        )
    return current_user


def require_admin(
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """
    Require admin role
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


# ============================================================
# Common Query Parameters
# ============================================================

class CommonQueryParams:
    """
    Common query parameters for listing endpoints
    """
    def __init__(
        self,
        q: Optional[str] = Query(default=None, description="Search query"),
        sort_by: Optional[str] = Query(default=None, description="Sort field"),
        sort_order: str = Query(default="asc", pattern="^(asc|desc)$")
    ):
        self.q = q
        self.sort_by = sort_by
        self.sort_order = sort_order
