# Level 12: Middleware

## Learning Objectives
- Understand what middleware is and when to use it
- Create function-based middleware
- Create class-based middleware
- Configure CORS middleware
- Build logging and timing middleware
- Handle errors in middleware
- Add security headers
- Implement rate limiting

---

## Setup Instructions

```bash
cd level_12_middleware
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## What is Middleware?

Middleware is code that runs **before** and/or **after** every request.

```
Request Flow:
┌────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────┐
│ Client │ → │ Middleware 1 │ → │ Middleware 2 │ → │ Endpoint │
└────────┘   └──────────────┘   └──────────────┘   └──────────┘

Response Flow:
┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────┐
│ Endpoint │ → │ Middleware 2 │ → │ Middleware 1 │ → │ Client │
└──────────┘   └──────────────┘   └──────────────┘   └────────┘
```

**Common Use Cases:**
- Request logging
- Adding headers (request ID, timing)
- Authentication
- CORS handling
- Rate limiting
- Error handling

---

## Key Concepts

### 1. Function-Based Middleware
```python
@app.middleware("http")
async def my_middleware(request: Request, call_next):
    # BEFORE: Code here runs before endpoint
    print(f"Request: {request.method} {request.url}")
    
    # Call the endpoint
    response = await call_next(request)
    
    # AFTER: Code here runs after endpoint
    response.headers["X-Custom"] = "value"
    
    return response
```

### 2. Class-Based Middleware
```python
from starlette.middleware.base import BaseHTTPMiddleware

class MyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, some_config: str = "default"):
        super().__init__(app)
        self.some_config = some_config
    
    async def dispatch(self, request: Request, call_next):
        # Before
        response = await call_next(request)
        # After
        return response

# Add to app
app.add_middleware(MyMiddleware, some_config="value")
```

### 3. CORS Middleware
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Request ID Middleware
```python
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response
```

### 5. Timing Middleware
```python
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    
    response.headers["X-Process-Time-MS"] = str(duration_ms)
    return response
```

### 6. Error Handling Middleware
```python
class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
```

### 7. Security Headers Middleware
```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response
```

### 8. Rate Limiting Middleware
```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60):
        super().__init__(app)
        self.limit = limit
        self.requests = {}
    
    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        # Check and enforce rate limit
        # ...
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
```

---

## Middleware Execution Order

**Important:** Middleware added **last** runs **first**!

```python
app.add_middleware(MiddlewareA)  # Runs 2nd
app.add_middleware(MiddlewareB)  # Runs 1st

# Order: Request → B → A → Endpoint → A → B → Response
```

---

## Request State

Store data in `request.state` to share between middleware and endpoints:

```python
# In middleware
request.state.user_id = "123"
request.state.request_id = "abc"

# In endpoint
@app.get("/")
def endpoint(request: Request):
    user_id = request.state.user_id
    return {"user": user_id}
```

---

## CORS Configuration

| Option | Description |
|--------|-------------|
| `allow_origins` | List of allowed origins |
| `allow_credentials` | Allow cookies/auth headers |
| `allow_methods` | Allowed HTTP methods |
| `allow_headers` | Allowed request headers |
| `expose_headers` | Headers accessible to JS |
| `max_age` | Cache preflight response |

**Development (allow all):**
```python
allow_origins=["*"]
```

**Production (specific origins):**
```python
allow_origins=[
    "https://myapp.com",
    "https://admin.myapp.com"
]
```

---

## Test the Middleware

### Check Response Headers
```bash
curl -v http://localhost:8000/tasks
```

Look for:
- `X-Request-ID`
- `X-Process-Time-MS`
- `X-Content-Type-Options`
- `X-Frame-Options`

### Test Timing
```bash
curl -v http://localhost:8000/slow
# Check X-Process-Time-MS header (~1000ms)
```

### Test Error Handling
```bash
curl http://localhost:8000/error
# Returns JSON error instead of HTML
```

---

## Common Middleware Patterns

### Authentication Check
```python
class AuthMiddleware(BaseHTTPMiddleware):
    EXCLUDED = {"/", "/login", "/docs"}
    
    async def dispatch(self, request, call_next):
        if request.url.path not in self.EXCLUDED:
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        return await call_next(request)
```

### Request Logging
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### Compression (use built-in)
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## Exercises

### Exercise 1: Request Counter
Create middleware that:
- Counts total requests since startup
- Returns count in `X-Total-Requests` header

### Exercise 2: Maintenance Mode
Create middleware that:
- Checks a `MAINTENANCE_MODE` flag
- Returns 503 with message if enabled
- Allows requests to `/health` endpoint

### Exercise 3: Request Size Limiter
Create middleware that:
- Checks `Content-Length` header
- Returns 413 if body exceeds limit

### Exercise 4: Response Compression Logger
Create middleware that:
- Logs original vs compressed response size
- Adds `X-Original-Size` header

---

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| Forgetting `await call_next()` | Always await the call_next |
| Modifying response after return | Modify before returning |
| Reading body multiple times | Body can only be read once |
| Wrong middleware order | Remember: last added = first run |

---

## Best Practices

1. **Keep middleware focused** - One responsibility each
2. **Handle errors** - Don't let exceptions crash
3. **Be careful with body** - Can only read once
4. **Log appropriately** - Don't log sensitive data
5. **Consider performance** - Middleware runs on every request
6. **Order matters** - Add in correct sequence

---

## What's Next?
**Level 13: Background Tasks** - Learn to run tasks in the background without blocking responses.
