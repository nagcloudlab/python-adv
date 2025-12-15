"""
Level 8: Headers & Cookies
==========================
Concepts Covered:
    - Reading request headers with Header()
    - Setting response headers
    - Reading cookies with Cookie()
    - Setting cookies in response
    - Common header patterns (Authorization, API Key, etc.)
    - CORS headers basics
    - Custom headers (X- prefix)

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs (Swagger UI)
    Use browser DevTools Network tab to see headers/cookies
"""

from fastapi import FastAPI, Header, Cookie, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Annotated
from datetime import datetime, timedelta
import secrets

app = FastAPI(
    title="Task Manager API - Level 8",
    description="Learning Headers & Cookies",
    version="8.0.0"
)


# ============================================================
# CONCEPT 1: Reading Request Headers
# ============================================================
# Header() reads HTTP headers
# FastAPI automatically converts header names:
#   user-agent → user_agent (hyphen to underscore)

@app.get("/headers/basic")
def read_basic_headers(
    user_agent: Annotated[Optional[str], Header()] = None,
    accept: Annotated[Optional[str], Header()] = None,
    host: Annotated[Optional[str], Header()] = None
):
    """
    Read common request headers
    
    Headers are automatically converted:
    - User-Agent → user_agent
    - Accept → accept
    - Host → host
    """
    return {
        "user_agent": user_agent,
        "accept": accept,
        "host": host
    }


# Custom headers (X- prefix convention)
@app.get("/headers/custom")
def read_custom_headers(
    x_token: Annotated[Optional[str], Header()] = None,
    x_request_id: Annotated[Optional[str], Header()] = None,
    x_client_version: Annotated[Optional[str], Header()] = None
):
    """
    Read custom headers (X- prefix)
    
    Custom headers typically use X- prefix:
    - X-Token → x_token
    - X-Request-ID → x_request_id
    - X-Client-Version → x_client_version
    """
    return {
        "x_token": x_token,
        "x_request_id": x_request_id,
        "x_client_version": x_client_version
    }


# ============================================================
# CONCEPT 2: Required Headers
# ============================================================

@app.get("/headers/required")
def required_header(
    x_api_key: Annotated[str, Header(description="API Key - Required")]
):
    """
    Endpoint requiring API key header
    
    Send header: X-API-Key: your-api-key
    Without header → 422 Validation Error
    """
    # Validate API key (simplified)
    if len(x_api_key) < 10:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return {
        "message": "API key accepted",
        "key_preview": x_api_key[:4] + "****"
    }


# ============================================================
# CONCEPT 3: Authorization Header
# ============================================================

@app.get("/headers/auth")
def authorization_header(
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Read Authorization header
    
    Common formats:
    - Bearer <token>
    - Basic <base64>
    - ApiKey <key>
    
    Example: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    """
    if not authorization:
        return {"authenticated": False, "message": "No authorization header"}
    
    # Parse authorization type
    parts = authorization.split(" ", 1)
    auth_type = parts[0] if parts else None
    auth_value = parts[1] if len(parts) > 1 else None
    
    return {
        "authenticated": True,
        "auth_type": auth_type,
        "token_preview": auth_value[:20] + "..." if auth_value and len(auth_value) > 20 else auth_value
    }


# ============================================================
# CONCEPT 4: Multiple Header Values
# ============================================================
# Some headers can have multiple values

@app.get("/headers/multiple")
def multiple_header_values(
    x_forwarded_for: Annotated[Optional[List[str]], Header()] = None
):
    """
    Read header with multiple values
    
    X-Forwarded-For can have multiple IPs:
    X-Forwarded-For: client, proxy1, proxy2
    """
    return {
        "forwarded_for": x_forwarded_for,
        "client_ip": x_forwarded_for[0] if x_forwarded_for else None
    }


# ============================================================
# CONCEPT 5: Setting Response Headers
# ============================================================

@app.get("/headers/set")
def set_response_headers(response: Response):
    """
    Set custom response headers
    
    Use Response parameter to add headers
    Check response headers in browser DevTools
    """
    # Set custom headers
    response.headers["X-Custom-Header"] = "custom-value"
    response.headers["X-Request-Time"] = datetime.now().isoformat()
    response.headers["X-API-Version"] = "8.0.0"
    response.headers["X-Rate-Limit-Remaining"] = "99"
    
    return {
        "message": "Check response headers!",
        "headers_set": [
            "X-Custom-Header",
            "X-Request-Time",
            "X-API-Version",
            "X-Rate-Limit-Remaining"
        ]
    }


# Using JSONResponse for headers
@app.get("/headers/json-response")
def set_headers_with_json_response():
    """
    Set headers using JSONResponse
    
    Alternative way to set response headers
    """
    content = {
        "message": "Response with custom headers",
        "timestamp": datetime.now().isoformat()
    }
    
    headers = {
        "X-Custom-Header": "my-value",
        "X-Total-Count": "100",
        "X-Page": "1",
        "X-Per-Page": "10"
    }
    
    return JSONResponse(content=content, headers=headers)


# ============================================================
# CONCEPT 6: Reading Cookies
# ============================================================

@app.get("/cookies/read")
def read_cookies(
    session_id: Annotated[Optional[str], Cookie()] = None,
    user_pref: Annotated[Optional[str], Cookie()] = None,
    theme: Annotated[Optional[str], Cookie()] = None
):
    """
    Read cookies from request
    
    Cookies are sent automatically by browser
    Cookie names use underscore (session_id → session_id cookie)
    """
    return {
        "session_id": session_id,
        "user_pref": user_pref,
        "theme": theme,
        "has_session": session_id is not None
    }


# ============================================================
# CONCEPT 7: Setting Cookies
# ============================================================

@app.post("/cookies/set")
def set_cookies(response: Response):
    """
    Set cookies in response
    
    Cookies will be stored by browser and sent with subsequent requests
    """
    # Generate session ID
    session_id = secrets.token_hex(16)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,      # Not accessible via JavaScript
        max_age=3600,       # 1 hour
        samesite="lax"      # CSRF protection
    )
    
    # Set preferences cookie
    response.set_cookie(
        key="theme",
        value="dark",
        max_age=86400 * 30  # 30 days
    )
    
    # Set user preference
    response.set_cookie(
        key="user_pref",
        value="compact_view",
        max_age=86400 * 30
    )
    
    return {
        "message": "Cookies set successfully",
        "session_id": session_id,
        "cookies_set": ["session_id", "theme", "user_pref"]
    }


# ============================================================
# CONCEPT 8: Cookie Options
# ============================================================

@app.post("/cookies/secure")
def set_secure_cookie(response: Response):
    """
    Set cookie with all security options
    
    Cookie attributes:
    - httponly: Not accessible via JavaScript (XSS protection)
    - secure: Only sent over HTTPS
    - samesite: CSRF protection (strict, lax, none)
    - max_age: Expiration in seconds
    - path: URL path scope
    - domain: Domain scope
    """
    token = secrets.token_hex(32)
    
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,          # Can't access via document.cookie
        secure=False,           # Set True in production (HTTPS only)
        samesite="strict",      # Strictest CSRF protection
        max_age=3600,           # 1 hour
        path="/",               # Available on all paths
        # domain=".example.com" # Uncomment for subdomain access
    )
    
    return {
        "message": "Secure cookie set",
        "token_preview": token[:8] + "...",
        "attributes": {
            "httponly": True,
            "secure": "False (set True in production)",
            "samesite": "strict",
            "max_age": "3600 seconds",
            "path": "/"
        }
    }


# ============================================================
# CONCEPT 9: Delete Cookies
# ============================================================

@app.post("/cookies/delete")
def delete_cookies(response: Response):
    """
    Delete cookies
    
    Deleting sets the cookie with immediate expiration
    """
    response.delete_cookie(key="session_id")
    response.delete_cookie(key="theme")
    response.delete_cookie(key="user_pref")
    
    return {
        "message": "Cookies deleted",
        "deleted": ["session_id", "theme", "user_pref"]
    }


# ============================================================
# CONCEPT 10: Practical Example - Simple Auth Flow
# ============================================================

# Simulated user database
users_db = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

# Active sessions
sessions_db = {}


@app.post("/auth/login")
def login(
    response: Response,
    username: str,
    password: str
):
    """
    Login endpoint - creates session cookie
    
    Test with:
    - username: admin, password: admin123
    - username: user, password: user123
    """
    # Validate credentials
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session
    session_id = secrets.token_hex(16)
    sessions_db[session_id] = {
        "username": username,
        "role": user["role"],
        "created_at": datetime.now().isoformat()
    }
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=3600,
        samesite="lax"
    )
    
    return {
        "message": "Login successful",
        "username": username,
        "role": user["role"]
    }


@app.get("/auth/me")
def get_current_user(
    session_id: Annotated[Optional[str], Cookie()] = None
):
    """
    Get current user from session cookie
    
    Requires valid session cookie from /auth/login
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return {
        "authenticated": True,
        "username": session["username"],
        "role": session["role"],
        "session_created": session["created_at"]
    }


@app.post("/auth/logout")
def logout(
    response: Response,
    session_id: Annotated[Optional[str], Cookie()] = None
):
    """
    Logout - delete session cookie
    """
    if session_id and session_id in sessions_db:
        del sessions_db[session_id]
    
    response.delete_cookie(key="session_id")
    
    return {"message": "Logged out successfully"}


# ============================================================
# CONCEPT 11: API Key in Header Pattern
# ============================================================

API_KEYS = {
    "key-12345-abcde": {"user": "app1", "tier": "premium"},
    "key-67890-fghij": {"user": "app2", "tier": "basic"}
}


@app.get("/api/data")
def get_protected_data(
    x_api_key: Annotated[str, Header(description="API Key")]
):
    """
    Protected endpoint using API key header
    
    Send header: X-API-Key: key-12345-abcde
    """
    key_info = API_KEYS.get(x_api_key)
    
    if not key_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return {
        "message": "Access granted",
        "user": key_info["user"],
        "tier": key_info["tier"],
        "data": {
            "tasks_count": 42,
            "users_count": 10
        }
    }


# ============================================================
# CONCEPT 12: Request Metadata Headers
# ============================================================

@app.get("/headers/metadata")
def request_metadata(
    host: Annotated[Optional[str], Header()] = None,
    user_agent: Annotated[Optional[str], Header()] = None,
    accept_language: Annotated[Optional[str], Header()] = None,
    accept_encoding: Annotated[Optional[str], Header()] = None,
    connection: Annotated[Optional[str], Header()] = None,
    content_type: Annotated[Optional[str], Header()] = None,
    referer: Annotated[Optional[str], Header()] = None,
    origin: Annotated[Optional[str], Header()] = None
):
    """
    Read various request metadata headers
    
    These headers provide info about the client and request
    """
    return {
        "host": host,
        "user_agent": user_agent,
        "accept_language": accept_language,
        "accept_encoding": accept_encoding,
        "connection": connection,
        "content_type": content_type,
        "referer": referer,
        "origin": origin
    }


# ============================================================
# CONCEPT 13: Disable Header Auto-Conversion
# ============================================================

@app.get("/headers/raw")
def raw_header(
    strange_header: Annotated[Optional[str], Header(convert_underscores=False)] = None
):
    """
    Read header without auto-conversion
    
    By default: some-header → some_header
    With convert_underscores=False: header name used as-is
    
    Send: strange_header: value (exact name)
    """
    return {"strange_header": strange_header}


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 8 - Headers & Cookies",
        "concepts": [
            "Header() - Read request headers",
            "Cookie() - Read cookies",
            "Response.headers - Set response headers",
            "Response.set_cookie() - Set cookies",
            "Response.delete_cookie() - Delete cookies"
        ],
        "test_endpoints": {
            "headers": [
                "GET /headers/basic - Read common headers",
                "GET /headers/custom - Read X- headers",
                "GET /headers/required - Required header",
                "GET /headers/auth - Authorization header",
                "GET /headers/set - Set response headers",
                "GET /headers/metadata - Request metadata"
            ],
            "cookies": [
                "GET /cookies/read - Read cookies",
                "POST /cookies/set - Set cookies",
                "POST /cookies/secure - Secure cookie",
                "POST /cookies/delete - Delete cookies"
            ],
            "auth_flow": [
                "POST /auth/login?username=admin&password=admin123",
                "GET /auth/me - Check session",
                "POST /auth/logout"
            ],
            "api_key": [
                "GET /api/data (X-API-Key: key-12345-abcde)"
            ]
        }
    }
