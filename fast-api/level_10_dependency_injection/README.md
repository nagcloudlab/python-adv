# Level 10: Dependency Injection

## Learning Objectives
- Understand dependency injection pattern
- Create function-based dependencies
- Create class-based dependencies
- Chain/nest dependencies
- Use dependencies with yield for cleanup
- Apply path operation dependencies
- Configure global dependencies
- Override dependencies for testing

---

## Setup Instructions

```bash
cd level_10_dependency_injection
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## What is Dependency Injection?

Dependency Injection (DI) is a pattern where components receive their dependencies from external sources rather than creating them internally.

**Benefits:**
- Code reusability
- Easier testing (mock dependencies)
- Separation of concerns
- Cleaner endpoint code

---

## Key Concepts

### 1. Basic Function Dependency
```python
from fastapi import Depends

def get_pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/items")
def list_items(params: dict = Depends(get_pagination)):
    return {"pagination": params}
```

### 2. Validation Dependency
```python
def validate_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Not found")
    return items_db[item_id]

@app.get("/items/{item_id}")
def get_item(item: dict = Depends(validate_item)):
    return item  # Already validated!
```

### 3. Authentication Dependency
```python
def get_current_user(token: str = Header()):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get("/profile")
def profile(user: dict = Depends(get_current_user)):
    return user

@app.get("/dashboard")
def profile(user: dict = Depends(get_current_user)):
    return user

@app.get("/settings")
def profile(user: dict = Depends(get_current_user)):
    return user    
```

### 4. Chained Dependencies
```python
def get_api_key(x_api_key: str = Header()):
    return x_api_key

def get_user(api_key: str = Depends(get_api_key)):
    user = find_user_by_key(api_key)
    return user

def require_admin(user: dict = Depends(get_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403)
    return user

@app.delete("/items/{id}")
def delete_item(admin: dict = Depends(require_admin)):
    # Only admins reach here
    pass
```

### 5. Class-Based Dependency
```python
class Pagination:
    def __init__(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100)
    ):
        self.skip = skip
        self.limit = limit

@app.get("/items")
def list_items(pagination: Pagination = Depends()):
    # Depends() without args uses class __init__
    return {"skip": pagination.skip, "limit": pagination.limit}
```

### 6. Callable Class Dependency
```python
class RoleChecker:
    def __init__(self, required_role: str):
        self.required_role = required_role
    
    def __call__(self, user: dict = Depends(get_current_user)):
        if user["role"] != self.required_role:
            raise HTTPException(status_code=403)
        return user

# Create configured instances
require_admin = RoleChecker("admin")
require_manager = RoleChecker("manager")

@app.get("/admin/dashboard")
def admin_dashboard(user: dict = Depends(require_admin)):
    return {"admin": user["username"]}
```

### 7. Dependency with Yield (Cleanup)
```python
def get_db():
    db = Database()
    db.connect()
    try:
        yield db  # Endpoint receives this
    finally:
        db.disconnect()  # Always runs (cleanup)

@app.get("/items")
def list_items(db: Database = Depends(get_db)):
    return db.query("SELECT * FROM items")
```

**Flow:**
1. `db.connect()` runs
2. `db` is passed to endpoint
3. Endpoint executes
4. `db.disconnect()` runs (even on error)

### 8. Path Operation Dependencies
```python
def verify_token(token: str = Header()):
    if not valid_token(token):
        raise HTTPException(status_code=401)

def log_request():
    print(f"Request at {datetime.now()}")

@app.get(
    "/items",
    dependencies=[Depends(verify_token), Depends(log_request)]
)
def list_items():
    # Dependencies ran, but we don't use their return values
    return {"items": [...]}
```

### 9. Global Dependencies
```python
app = FastAPI(
    dependencies=[
        Depends(verify_api_key),
        Depends(rate_limit)
    ]
)

# Now ALL endpoints require these dependencies
```

### 10. Dependency Overrides (Testing)
```python
# In your test file:
from main import app, get_db

def mock_db():
    return FakeDatabase()

app.dependency_overrides[get_db] = mock_db

# Now tests use FakeDatabase instead of real DB
```

---

## Dependency Types Comparison

| Type | Use Case | Example |
|------|----------|---------|
| Function | Simple logic | `def get_params()` |
| Class | Stateful/complex | `class Pagination` |
| Callable Class | Configurable | `RoleChecker("admin")` |
| With Yield | Resource cleanup | DB connections |

---

## Common Patterns

### Pattern 1: Database Session
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Pattern 2: Current User
```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return user
```

### Pattern 3: Pagination
```python
class Pagination:
    def __init__(self, page: int = 1, size: int = 10):
        self.skip = (page - 1) * size
        self.limit = size
```

### Pattern 4: Feature Flags
```python
class FeatureFlag:
    def __init__(self, feature: str):
        self.feature = feature
    
    def __call__(self):
        if not is_enabled(self.feature):
            raise HTTPException(status_code=404)

require_beta = FeatureFlag("beta_features")
```

---

## Test API Keys

| User | API Key | Role |
|------|---------|------|
| admin | `admin-key-12345` | admin |
| user1 | `user1-key-67890` | user |

**Header:** `X-API-Key: admin-key-12345`

---

## Test Scenarios

### Basic Dependency
```bash
curl "http://localhost:8000/tasks?skip=0&limit=5"
```

### Auth Dependency
```bash
curl -H "X-API-Key: admin-key-12345" http://localhost:8000/users/me
```

### Admin Only
```bash
# As admin (works)
curl -X DELETE -H "X-API-Key: admin-key-12345" http://localhost:8000/tasks/1

# As user (403 Forbidden)
curl -X DELETE -H "X-API-Key: user1-key-67890" http://localhost:8000/tasks/1
```

### Database Dependency
```bash
curl http://localhost:8000/db/tasks
# Check console for connect/disconnect logs
```

---

## Exercises

### Exercise 1: Logger Dependency
Create a dependency that logs:
- Request timestamp
- Endpoint path
- User (if authenticated)

### Exercise 2: Rate Limiter
Create a class-based rate limiter:
- Configurable limit per minute
- Track by API key
- Return `X-RateLimit-Remaining` header

### Exercise 3: Feature Toggle
Create a dependency that:
- Reads feature flags from config
- Returns 404 if feature disabled
- Works as callable class

### Exercise 4: Audit Trail
Create a dependency with yield that:
- Records request start time
- After endpoint: logs duration and status

---

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| `Depends(func())` | `Depends(func)` - no parentheses on function |
| Forgetting `yield` cleanup | Use try/finally with yield |
| Circular dependencies | Restructure dependency chain |
| Heavy logic in dependencies | Keep dependencies focused |

---

## Best Practices

1. **Keep dependencies focused** - One responsibility each
2. **Use yield for resources** - Ensures cleanup
3. **Chain for complex auth** - Build up from simple deps
4. **Use class deps for config** - When you need parameters
5. **Override in tests** - Mock external services
6. **Document dependencies** - What they require/return

---

## What's Next?
**Level 11: Security & Authentication** - Learn OAuth2, JWT tokens, password hashing, and secure authentication flows.
