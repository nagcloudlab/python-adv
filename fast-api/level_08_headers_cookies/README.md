# Level 8: Headers & Cookies

## Learning Objectives
- Read request headers with `Header()`
- Set response headers
- Read cookies with `Cookie()`
- Set and delete cookies
- Implement API key authentication
- Build session-based authentication flow
- Understand cookie security options

---

## Setup Instructions

```bash
cd level_08_headers_cookies
pip install -r requirements.txt
uvicorn main:app --reload
```

**Testing Tips:**
- Use Swagger UI at `/docs` for API testing
- Use browser DevTools → Network tab to see headers
- Use browser DevTools → Application → Cookies to see cookies

---

## Key Concepts

### 1. Reading Headers
```python
from fastapi import Header
from typing import Annotated, Optional

@app.get("/headers")
def read_headers(
    user_agent: Annotated[Optional[str], Header()] = None,
    x_token: Annotated[Optional[str], Header()] = None
):
    return {"user_agent": user_agent, "x_token": x_token}
```

**Header Name Conversion:**
| HTTP Header | Python Parameter |
|-------------|------------------|
| `User-Agent` | `user_agent` |
| `X-Token` | `x_token` |
| `Accept-Language` | `accept_language` |

### 2. Required Headers
```python
@app.get("/protected")
def protected(
    x_api_key: Annotated[str, Header()]  # No default = required
):
    return {"key": x_api_key}
```

### 3. Authorization Header
```python
@app.get("/auth")
def auth(
    authorization: Annotated[Optional[str], Header()] = None
):
    # Parse: "Bearer <token>" or "Basic <base64>"
    if authorization:
        auth_type, token = authorization.split(" ", 1)
        return {"type": auth_type, "token": token}
    return {"authenticated": False}
```

### 4. Setting Response Headers
```python
from fastapi import Response

@app.get("/data")
def get_data(response: Response):
    response.headers["X-Custom-Header"] = "value"
    response.headers["X-Request-ID"] = "12345"
    return {"data": "content"}
```

### 5. Using JSONResponse
```python
from fastapi.responses import JSONResponse

@app.get("/data")
def get_data():
    return JSONResponse(
        content={"data": "content"},
        headers={"X-Custom": "value"}
    )
```

### 6. Reading Cookies
```python
from fastapi import Cookie

@app.get("/cookies")
def read_cookies(
    session_id: Annotated[Optional[str], Cookie()] = None,
    theme: Annotated[Optional[str], Cookie()] = None
):
    return {"session_id": session_id, "theme": theme}
```

### 7. Setting Cookies
```python
@app.post("/login")
def login(response: Response):
    response.set_cookie(
        key="session_id",
        value="abc123",
        httponly=True,      # JS can't access
        max_age=3600,       # 1 hour
        samesite="lax"      # CSRF protection
    )
    return {"message": "Logged in"}
```

### 8. Cookie Security Options

| Option | Purpose | Value |
|--------|---------|-------|
| `httponly` | Prevent JS access (XSS protection) | `True` |
| `secure` | HTTPS only | `True` (production) |
| `samesite` | CSRF protection | `"strict"`, `"lax"`, `"none"` |
| `max_age` | Expiration (seconds) | `3600` (1 hour) |
| `path` | URL path scope | `"/"` |
| `domain` | Domain scope | `".example.com"` |

### 9. Deleting Cookies
```python
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session_id")
    return {"message": "Logged out"}
```

---

## Common HTTP Headers

### Request Headers
| Header | Purpose |
|--------|---------|
| `Authorization` | Auth credentials (Bearer, Basic) |
| `Content-Type` | Request body format |
| `Accept` | Acceptable response formats |
| `User-Agent` | Client application info |
| `X-API-Key` | API key authentication |
| `X-Request-ID` | Request tracking |

### Response Headers
| Header | Purpose |
|--------|---------|
| `Content-Type` | Response body format |
| `Set-Cookie` | Set browser cookie |
| `X-RateLimit-Remaining` | Rate limit info |
| `X-Total-Count` | Pagination total |
| `Cache-Control` | Caching directives |

---

## SameSite Cookie Values

| Value | Behavior |
|-------|----------|
| `strict` | Cookie only sent for same-site requests |
| `lax` | Cookie sent for same-site + top-level navigation |
| `none` | Cookie always sent (requires `secure=True`) |

---

## Authentication Patterns

### Pattern 1: API Key Header
```python
@app.get("/api/data")
def protected_data(
    x_api_key: Annotated[str, Header()]
):
    if x_api_key != "valid-key":
        raise HTTPException(status_code=401)
    return {"data": "secret"}
```

### Pattern 2: Session Cookie
```python
# Login - set cookie
@app.post("/login")
def login(response: Response, username: str, password: str):
    session_id = create_session(username)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return {"message": "Logged in"}

# Protected route - read cookie
@app.get("/profile")
def profile(session_id: Annotated[Optional[str], Cookie()] = None):
    if not session_id or not valid_session(session_id):
        raise HTTPException(status_code=401)
    return {"user": get_user_from_session(session_id)}
```

### Pattern 3: Bearer Token
```python
@app.get("/profile")
def profile(authorization: Annotated[Optional[str], Header()] = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    return {"user": user}
```

---

## Test Scenarios

### Test Headers
```bash
# Read headers
curl http://localhost:8000/headers/basic

# With custom header
curl -H "X-API-Key: my-key" http://localhost:8000/headers/required

# With Authorization
curl -H "Authorization: Bearer my-token" http://localhost:8000/headers/auth
```

### Test Cookies (Use Browser)
1. Open http://localhost:8000/docs
2. Call `POST /cookies/set`
3. Check DevTools → Application → Cookies
4. Call `GET /cookies/read` to verify

### Test Auth Flow
1. `POST /auth/login?username=admin&password=admin123`
2. `GET /auth/me` (session cookie auto-sent)
3. `POST /auth/logout`

---

## Exercises

### Exercise 1: Rate Limiting Headers
Create endpoint that returns rate limit info:
- `X-RateLimit-Limit: 100`
- `X-RateLimit-Remaining: 95`
- `X-RateLimit-Reset: <timestamp>`

### Exercise 2: User Preferences Cookie
Create endpoints:
- `POST /preferences` - Set preferences cookie (JSON encoded)
- `GET /preferences` - Read and parse preferences

### Exercise 3: API Key with Tiers
Create tiered API access:
- Read `X-API-Key` header
- Return different data based on key tier (basic/premium)
- Set `X-Tier: basic` or `X-Tier: premium` in response

### Exercise 4: Request Tracking
Create middleware-like behavior:
- Generate `X-Request-ID` if not provided
- Echo `X-Request-ID` in response
- Add `X-Response-Time` header

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `422` on required header | Missing header | Include header in request |
| Cookie not sent | Different domain/path | Check cookie scope |
| Cookie not readable | `httponly=True` | Can't access via JS (by design) |
| Cookie not persisting | Missing `max_age` | Set expiration |

---

## Security Best Practices

1. **Always use `httponly=True`** for session cookies
2. **Use `secure=True`** in production (HTTPS)
3. **Use `samesite="strict"`** or `"lax"` for CSRF protection
4. **Never store sensitive data** in cookies (use session IDs)
5. **Validate all headers** server-side
6. **Set short expiration** for sensitive cookies
7. **Use HTTPS** for all authenticated endpoints

---

## What's Next?
**Level 9: Status Codes & Exception Handling** - Learn to return proper HTTP status codes, create custom exceptions, and handle errors gracefully.
