# Level 11: Security & Authentication

## Learning Objectives
- Hash passwords securely with bcrypt
- Implement OAuth2 Password flow
- Create and verify JWT tokens
- Protect routes with authentication
- Implement token refresh mechanism
- Build role-based access control
- Handle token logout/revocation

---

## Setup Instructions

```bash
cd level_11_security_auth
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Key Concepts

### 1. Password Hashing with Bcrypt
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Why bcrypt?**
- Includes salt automatically
- Same password → different hash each time
- Computationally expensive (slow to brute force)

### 2. OAuth2 Password Bearer Setup
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
```

- `tokenUrl` points to login endpoint
- Swagger UI shows "Authorize" button
- Automatically extracts `Authorization: Bearer <token>` header

### 3. JWT Token Creation
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    
    to_encode.update({"exp": expire, "type": "access"})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**JWT Structure:**
```
header.payload.signature

Payload contains:
- sub: Subject (username)
- exp: Expiration time
- iat: Issued at
- role: User role (optional)
```

### 4. Token Verification
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401)
    
    return user
```

### 5. Protected Routes
```python
@app.get("/users/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### 6. Role-Based Access Control
```python
def require_role(required_role: str):
    async def role_checker(user: User = Depends(get_current_active_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403)
        return user
    return role_checker

require_admin = require_role("admin")

@app.get("/admin/users")
def list_users(admin: User = Depends(require_admin)):
    return users
```

---

## Authentication Flow

```
┌──────────┐     POST /auth/token      ┌──────────┐
│  Client  │ ───────────────────────▶  │  Server  │
│          │     username + password   │          │
│          │                           │          │
│          │   ◀───────────────────── │          │
│          │     access_token +        │          │
│          │     refresh_token         │          │
└──────────┘                           └──────────┘
     │
     │  GET /users/me
     │  Authorization: Bearer <access_token>
     ▼
┌──────────┐                           ┌──────────┐
│  Client  │ ───────────────────────▶  │  Server  │
│          │                           │          │
│          │   ◀───────────────────── │          │
│          │     User data             │          │
└──────────┘                           └──────────┘
```

---

## Token Types

| Type | Purpose | Expiration |
|------|---------|------------|
| Access Token | API authentication | Short (15-30 min) |
| Refresh Token | Get new access token | Long (7-30 days) |

**Why two tokens?**
- Access token: Used frequently, short-lived for security
- Refresh token: Used only to get new access token

---

## Test Credentials

| User | Username | Password | Role |
|------|----------|----------|------|
| Admin | admin | admin123 | admin |
| Regular | john | john1234 | user |
| Disabled | disabled_user | disabled123 | user |

---

## Testing with Swagger UI

1. Open http://127.0.0.1:8000/docs
2. Click **"Authorize"** button (top right)
3. Enter username: `admin`, password: `admin123`
4. Click **"Authorize"**
5. Now all protected endpoints work!

---

## Testing with cURL

### 1. Login (Get Token)
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 2. Access Protected Route
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/users/me
```

### 3. Refresh Token
```bash
curl -X POST "http://localhost:8000/auth/refresh?refresh_token=<refresh_token>"
```

### 4. Logout
```bash
curl -X POST -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/auth/logout
```

---

## Security Best Practices

### DO ✅
- Use bcrypt for password hashing
- Use HTTPS in production
- Set short expiration for access tokens
- Store SECRET_KEY in environment variables
- Validate token type (access vs refresh)
- Implement token blacklist for logout

### DON'T ❌
- Store plain text passwords
- Use weak SECRET_KEY
- Set very long access token expiration
- Send tokens in URL parameters
- Store sensitive data in JWT payload

---

## JWT Payload Example

```json
{
  "sub": "admin",
  "role": "admin",
  "exp": 1704067200,
  "iat": 1704065400,
  "type": "access"
}
```

| Claim | Meaning |
|-------|---------|
| `sub` | Subject (username) |
| `role` | User role |
| `exp` | Expiration timestamp |
| `iat` | Issued at timestamp |
| `type` | Token type |

---

## Exercises

### Exercise 1: Email Verification
Add email verification flow:
- Generate verification token on registration
- Create `/auth/verify-email?token=...` endpoint
- Mark user as verified

### Exercise 2: Password Reset
Implement password reset:
- `POST /auth/forgot-password` (send reset email)
- `POST /auth/reset-password` (with token)

### Exercise 3: Two-Factor Auth
Add 2FA:
- Generate TOTP secret on enable
- Require code on login
- Backup codes

### Exercise 4: API Key Auth
Add API key authentication:
- Generate API keys for users
- Support both JWT and API key auth

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired token | Login again |
| 403 Forbidden | Insufficient role | Use account with correct role |
| "Could not validate credentials" | Token decode failed | Check token format |
| "Inactive user" | User is disabled | Contact admin |

---

## Production Checklist

- [ ] Use environment variables for SECRET_KEY
- [ ] Use HTTPS only
- [ ] Set appropriate token expiration times
- [ ] Implement rate limiting on login
- [ ] Log authentication failures
- [ ] Use secure cookie settings for web apps
- [ ] Consider refresh token rotation
- [ ] Implement account lockout after failed attempts

---

## What's Next?
**Level 12: Middleware** - Learn to create custom middleware for logging, CORS, request processing, and more.
