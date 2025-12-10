"""
Level 12: Middleware
====================
Concepts Covered:
    - What is middleware
    - Creating custom middleware
    - CORS middleware
    - Request/Response processing
    - Logging middleware
    - Timing middleware
    - Error handling middleware
    - Adding custom headers
    - Middleware execution order

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Task Manager API - Level 12",
    description="Learning Middleware",
    version="12.0.0"
)


# ============================================================
# CONCEPT 1: What is Middleware?
# ============================================================
"""
Middleware is code that runs BEFORE and/or AFTER every request.

Request Flow:
    Client → Middleware1 → Middleware2 → ... → Endpoint
    
Response Flow:
    Endpoint → ... → Middleware2 → Middleware1 → Client

Use cases:
- Logging requests
- Adding headers
- Authentication
- CORS handling
- Rate limiting
- Request timing
- Error handling
"""


# ============================================================
# CONCEPT 2: Simple Function-Based Middleware
# ============================================================

@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable):
    """
    Add unique request ID to every request/response
    
    - Runs BEFORE request reaches endpoint
    - Calls endpoint via call_next()
    - Runs AFTER response is generated
    """
    # BEFORE: Generate request ID
    request_id = str(uuid.uuid4())[:8]
    
    # Store in request state (accessible in endpoints)
    request.state.request_id = request_id
    
    # Log incoming request
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    # Call the actual endpoint
    response = await call_next(request)
    
    # AFTER: Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


@app.middleware("http")
async def timing_middleware(request: Request, call_next: Callable):
    """
    Measure and log request processing time
    """
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    duration_ms = round(duration * 1000, 2)
    
    # Add timing header
    response.headers["X-Process-Time-MS"] = str(duration_ms)
    
    # Log timing
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] Completed in {duration_ms}ms")
    
    return response


# ============================================================
# CONCEPT 3: CORS Middleware (Built-in)
# ============================================================
"""
CORS = Cross-Origin Resource Sharing
Allows/restricts which domains can access your API

Important for:
- Frontend apps on different domains
- Mobile apps
- Third-party integrations
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:8080",      # Vue dev server
        "https://myapp.example.com",  # Production frontend
    ],
    allow_credentials=True,           # Allow cookies
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
    expose_headers=[                  # Headers accessible to frontend JS
        "X-Request-ID",
        "X-Process-Time-MS"
    ]
)

# For development, allow all origins:
# allow_origins=["*"]


# ============================================================
# CONCEPT 4: Class-Based Middleware
# ============================================================

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Class-based middleware for detailed logging
    
    Benefits:
    - Can have __init__ for configuration
    - More structured than function-based
    - Can store state
    """
    
    def __init__(self, app, log_request_body: bool = False):
        super().__init__(app)
        self.log_request_body = log_request_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request details
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Client: {request.client.host if request.client else 'unknown'}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Optionally log body (careful with large bodies!)
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            logger.info(f"Body: {body.decode()[:500]}")  # First 500 chars
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(f"Response: {response.status_code}")
        
        return response


# Add class-based middleware
# Uncomment to enable detailed logging:
# app.add_middleware(LoggingMiddleware, log_request_body=True)


# ============================================================
# CONCEPT 5: Error Handling Middleware
# ============================================================

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Catch unhandled exceptions and return proper JSON responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Log the error
            request_id = getattr(request.state, 'request_id', 'unknown')
            logger.error(f"[{request_id}] Unhandled error: {exc}", exc_info=True)
            
            # Return JSON error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "request_id": request_id
                }
            )


# Add error handling middleware
app.add_middleware(ErrorHandlingMiddleware)


# ============================================================
# CONCEPT 6: Authentication Middleware
# ============================================================

class SimpleAuthMiddleware(BaseHTTPMiddleware):
    """
    Simple API key authentication middleware
    
    Checks X-API-Key header for all requests except excluded paths
    """
    
    VALID_API_KEYS = {"key-12345", "key-67890"}
    EXCLUDED_PATHS = {"/", "/docs", "/redoc", "/openapi.json", "/health"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Check API key
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "API key required", "header": "X-API-Key"}
            )
        
        if api_key not in self.VALID_API_KEYS:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key"}
            )
        
        # Store API key in request state
        request.state.api_key = api_key
        
        return await call_next(request)


# Uncomment to enable API key auth:
# app.add_middleware(SimpleAuthMiddleware)


# ============================================================
# CONCEPT 7: Rate Limiting Middleware
# ============================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting
    
    Note: For production, use Redis or similar
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # {ip: [(timestamp, count)]}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                t for t in self.requests[client_ip]
                if current_time - t < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Maximum {self.requests_per_minute} requests per minute",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self.requests[client_ip].append(current_time)
        
        # Add rate limit headers
        response = await call_next(request)
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


# Uncomment to enable rate limiting:
# app.add_middleware(RateLimitMiddleware, requests_per_minute=10)


# ============================================================
# CONCEPT 8: Request Modification Middleware
# ============================================================

@app.middleware("http")
async def normalize_headers(request: Request, call_next: Callable):
    """
    Middleware that processes/normalizes request data
    """
    # Example: Store lowercase path for case-insensitive routing
    request.state.normalized_path = request.url.path.lower()
    
    response = await call_next(request)
    return response


# ============================================================
# CONCEPT 9: Response Modification Middleware
# ============================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable):
    """
    Add security headers to all responses
    """
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Cache control (adjust as needed)
    if "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-store"
    
    return response


# ============================================================
# SAMPLE ENDPOINTS (to test middleware)
# ============================================================

@app.get("/")
def root():
    """Root endpoint - check response headers"""
    return {
        "message": "Level 12 - Middleware",
        "tip": "Check response headers in browser DevTools or curl -v"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/tasks")
def list_tasks(request: Request):
    """
    List tasks - shows request state from middleware
    """
    return {
        "tasks": [
            {"id": 1, "title": "Learn Middleware"},
            {"id": 2, "title": "Build API"},
        ],
        "request_id": getattr(request.state, 'request_id', None),
        "normalized_path": getattr(request.state, 'normalized_path', None)
    }


@app.get("/tasks/{task_id}")
def get_task(task_id: int, request: Request):
    """Get single task"""
    return {
        "id": task_id,
        "title": f"Task {task_id}",
        "request_id": getattr(request.state, 'request_id', None)
    }


@app.post("/tasks")
def create_task(title: str, request: Request):
    """Create task"""
    return {
        "message": "Task created",
        "title": title,
        "request_id": getattr(request.state, 'request_id', None)
    }


@app.get("/slow")
async def slow_endpoint():
    """
    Slow endpoint - demonstrates timing middleware
    
    Check X-Process-Time-MS header
    """
    import asyncio
    await asyncio.sleep(1)  # Simulate slow operation
    return {"message": "This took about 1 second"}


@app.get("/error")
def error_endpoint():
    """
    Endpoint that raises error - demonstrates error middleware
    """
    raise ValueError("This is a test error")


@app.get("/headers")
def show_headers(request: Request):
    """
    Show all request headers
    """
    return {
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else None
    }


@app.get("/middleware-info")
def middleware_info():
    """
    Information about active middleware
    """
    return {
        "active_middleware": [
            "add_request_id - Adds X-Request-ID header",
            "timing_middleware - Adds X-Process-Time-MS header",
            "add_security_headers - Adds security headers",
            "normalize_headers - Normalizes request path",
            "CORSMiddleware - Handles CORS",
            "ErrorHandlingMiddleware - Catches unhandled errors"
        ],
        "optional_middleware": [
            "LoggingMiddleware - Detailed request logging",
            "SimpleAuthMiddleware - API key authentication",
            "RateLimitMiddleware - Rate limiting"
        ],
        "execution_order": "Last added runs first (like a stack)"
    }


# ============================================================
# Root info
# ============================================================

@app.get("/info")
def info():
    """API Information"""
    return {
        "message": "Level 12 - Middleware",
        "concepts": [
            "Function-based middleware (@app.middleware)",
            "Class-based middleware (BaseHTTPMiddleware)",
            "CORS middleware",
            "Timing middleware",
            "Logging middleware",
            "Error handling middleware",
            "Security headers middleware",
            "Rate limiting middleware"
        ],
        "test_endpoints": [
            "GET / - Check response headers",
            "GET /tasks - See request_id in response",
            "GET /slow - Check X-Process-Time-MS header",
            "GET /error - Test error handling middleware",
            "GET /headers - See all request headers"
        ],
        "check_headers": [
            "X-Request-ID",
            "X-Process-Time-MS",
            "X-Content-Type-Options",
            "X-Frame-Options"
        ]
    }
