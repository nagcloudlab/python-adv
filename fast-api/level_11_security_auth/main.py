"""
Level 11: Security & Authentication
====================================
Concepts Covered:
    - Password hashing with passlib/bcrypt
    - OAuth2 Password flow
    - JWT (JSON Web Token) creation and verification
    - Protected routes with token authentication
    - Token refresh mechanism
    - Role-based access control
    - OAuth2 scopes

Installation:
    pip install python-jose[cryptography] passlib[bcrypt]

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs (Use "Authorize" button)
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Annotated
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI(
    title="Task Manager API - Level 11",
    description="Learning Security & Authentication",
    version="11.0.0"
)


# ============================================================
# CONFIGURATION
# ============================================================

# JWT Configuration
SECRET_KEY = "your-secret-key-keep-it-secret-in-production-use-env-vars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================
# CONCEPT 1: Password Hashing Setup
# ============================================================
# NEVER store plain text passwords!
# bcrypt is the recommended hashing algorithm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# CONCEPT 2: OAuth2 Password Bearer Setup
# ============================================================
# tokenUrl is the endpoint where users get their token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# ============================================================
# Models
# ============================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: Optional[str]
    role: str
    disabled: bool


class UserInDB(BaseModel):
    username: str
    email: str
    full_name: Optional[str]
    role: str
    disabled: bool
    hashed_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


# ============================================================
# Simulated Database
# ============================================================

# Pre-hash passwords for demo users
users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "disabled": False,
        "hashed_password": hash_password("admin123")
    },
    "john": {
        "username": "john",
        "email": "john@example.com",
        "full_name": "John Doe",
        "role": "user",
        "disabled": False,
        "hashed_password": hash_password("john1234")
    },
    "disabled_user": {
        "username": "disabled_user",
        "email": "disabled@example.com",
        "full_name": "Disabled User",
        "role": "user",
        "disabled": True,
        "hashed_password": hash_password("disabled123")
    }
}

# Token blacklist (for logout)
token_blacklist = set()


# ============================================================
# CONCEPT 3: JWT Token Creation
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data (usually {"sub": username})
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token (longer lived)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============================================================
# CONCEPT 4: User Authentication Functions
# ============================================================

def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user with username and password
    
    Returns user if credentials are valid, None otherwise
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ============================================================
# CONCEPT 5: Token Verification & Current User
# ============================================================

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    """
    Dependency to get current user from JWT token
    
    This is called automatically when endpoint uses Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Check if token is blacklisted (logged out)
    if token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None:
            raise credentials_exception
        
        # Ensure it's an access token, not refresh token
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        token_data = TokenData(username=username)
        
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserInDB:
    """
    Dependency to ensure user is not disabled
    
    Chains with get_current_user
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# ============================================================
# CONCEPT 6: Role-Based Access Control
# ============================================================

def require_role(required_role: str):
    """
    Factory function to create role-checking dependency
    """
    async def role_checker(
        current_user: Annotated[UserInDB, Depends(get_current_active_user)]
    ) -> UserInDB:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker


# Create specific role dependencies
require_admin = require_role("admin")


# ============================================================
# AUTH ENDPOINTS
# ============================================================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    """
    Register new user
    
    Password is hashed before storing
    """
    # Check if username exists
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user with hashed password
    new_user = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": "user",  # Default role
        "disabled": False,
        "hashed_password": hash_password(user.password)
    }
    
    users_db[user.username] = new_user
    
    return UserResponse(
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        role=new_user["role"],
        disabled=new_user["disabled"]
    )


@app.post("/auth/token", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    OAuth2 Password flow - Login endpoint
    
    This is the tokenUrl specified in OAuth2PasswordBearer
    
    Use form data (not JSON):
    - username: your username
    - password: your password
    
    Test credentials:
    - admin / admin123
    - john / john1234
    """
    # Authenticate user
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@app.post("/auth/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    
    Use when access token expires
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Verify user still exists and is active
    user = get_user(username)
    if not user or user.disabled:
        raise credentials_exception
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": username, "role": user.role}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": username}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@app.post("/auth/logout")
def logout(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Logout - Invalidate token
    
    Adds token to blacklist
    """
    token_blacklist.add(token)
    return {"message": "Successfully logged out"}


# ============================================================
# PROTECTED ENDPOINTS
# ============================================================

@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    """
    Get current user profile
    
    Requires valid access token
    """
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        disabled=current_user.disabled
    )


@app.put("/users/me")
def update_me(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    full_name: Optional[str] = None,
    email: Optional[EmailStr] = None
):
    """
    Update current user profile
    """
    user_data = users_db[current_user.username]
    
    if full_name:
        user_data["full_name"] = full_name
    if email:
        user_data["email"] = email
    
    return {"message": "Profile updated", "user": UserResponse(**user_data)}


@app.put("/users/me/password")
def change_password(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    current_password: str,
    new_password: str = Field(..., min_length=8)
):
    """
    Change current user's password
    """
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    users_db[current_user.username]["hashed_password"] = hash_password(new_password)
    
    return {"message": "Password changed successfully"}


# ============================================================
# ADMIN-ONLY ENDPOINTS
# ============================================================

@app.get("/admin/users", response_model=List[UserResponse])
def list_all_users(admin: Annotated[UserInDB, Depends(require_admin)]):
    """
    List all users - Admin only
    
    Requires admin role
    """
    return [
        UserResponse(
            username=u["username"],
            email=u["email"],
            full_name=u["full_name"],
            role=u["role"],
            disabled=u["disabled"]
        )
        for u in users_db.values()
    ]


@app.put("/admin/users/{username}/disable")
def disable_user(
    username: str,
    admin: Annotated[UserInDB, Depends(require_admin)]
):
    """
    Disable a user account - Admin only
    """
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if username == admin.username:
        raise HTTPException(
            status_code=400,
            detail="Cannot disable your own account"
        )
    
    users_db[username]["disabled"] = True
    return {"message": f"User '{username}' disabled"}


@app.put("/admin/users/{username}/enable")
def enable_user(
    username: str,
    admin: Annotated[UserInDB, Depends(require_admin)]
):
    """
    Enable a user account - Admin only
    """
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    users_db[username]["disabled"] = False
    return {"message": f"User '{username}' enabled"}


@app.put("/admin/users/{username}/role")
def change_user_role(
    username: str,
    new_role: str,
    admin: Annotated[UserInDB, Depends(require_admin)]
):
    """
    Change user role - Admin only
    """
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if new_role not in ["user", "admin", "moderator"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Allowed: user, admin, moderator"
        )
    
    users_db[username]["role"] = new_role
    return {"message": f"User '{username}' role changed to '{new_role}'"}


# ============================================================
# UTILITY ENDPOINTS
# ============================================================

@app.get("/auth/verify")
def verify_token_endpoint(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """
    Verify if token is valid
    
    Returns user info if token is valid
    """
    return {
        "valid": True,
        "username": current_user.username,
        "role": current_user.role
    }


@app.post("/auth/hash-password")
def demo_hash_password(password: str):
    """
    Demo endpoint to show password hashing
    
    Same password produces different hashes (bcrypt includes salt)
    """
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    return {
        "password": password,
        "hash1": hash1,
        "hash2": hash2,
        "hashes_are_different": hash1 != hash2,
        "but_both_verify": verify_password(password, hash1) and verify_password(password, hash2)
    }


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 11 - Security & Authentication",
        "concepts": [
            "Password hashing with bcrypt",
            "OAuth2 Password flow",
            "JWT access & refresh tokens",
            "Protected routes",
            "Role-based access control",
            "Token refresh & logout"
        ],
        "test_credentials": {
            "admin": {"username": "admin", "password": "admin123"},
            "user": {"username": "john", "password": "john1234"},
            "disabled": {"username": "disabled_user", "password": "disabled123"}
        },
        "auth_flow": [
            "1. POST /auth/token (login) → get access_token",
            "2. Use 'Authorize' button in Swagger UI",
            "3. Access protected endpoints",
            "4. POST /auth/refresh when token expires",
            "5. POST /auth/logout to invalidate token"
        ],
        "endpoints": {
            "public": [
                "POST /auth/register",
                "POST /auth/token",
                "POST /auth/refresh"
            ],
            "protected": [
                "GET /users/me",
                "PUT /users/me",
                "PUT /users/me/password",
                "POST /auth/logout"
            ],
            "admin_only": [
                "GET /admin/users",
                "PUT /admin/users/{username}/disable",
                "PUT /admin/users/{username}/enable",
                "PUT /admin/users/{username}/role"
            ]
        }
    }
