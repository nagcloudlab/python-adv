# Level 18: Lifespan Events

## Learning Objectives
- Understand application lifecycle
- Use lifespan context manager
- Initialize resources at startup
- Clean up resources at shutdown
- Manage database connections
- Implement cache warming
- Run background tasks
- Create health/readiness probes

---

## Setup Instructions

```bash
cd level_18_lifespan
pip install -r requirements.txt
uvicorn main:app --reload
```

**Watch the console** for startup/shutdown messages!

---

## Application Lifecycle

```
┌─────────────────────────────────────────────────┐
│                  APPLICATION                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  STARTUP                                         │
│  ├── Load configuration                          │
│  ├── Connect to database                         │
│  ├── Initialize cache                            │
│  ├── Start background tasks                      │
│  └── Mark as ready                               │
│                                                  │
│  ─────────────────────────────────────────────  │
│                                                  │
│  RUNNING (handling requests)                     │
│                                                  │
│  ─────────────────────────────────────────────  │
│                                                  │
│  SHUTDOWN                                        │
│  ├── Cancel background tasks                     │
│  ├── Close cache connections                     │
│  ├── Close database connections                  │
│  └── Final cleanup                               │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Key Concepts

### 1. Lifespan Context Manager (Modern)
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Code here runs before accepting requests
    print("Starting up...")
    db = await connect_database()
    
    yield  # App runs here
    
    # SHUTDOWN: Code here runs after last request
    print("Shutting down...")
    await db.disconnect()

app = FastAPI(lifespan=lifespan)
```

### 2. Application State
```python
class AppState:
    def __init__(self):
        self.db_pool = None
        self.cache = {}
        self.is_ready = False

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize
    app_state.db_pool = await create_pool()
    app_state.is_ready = True
    
    yield
    
    # Cleanup
    await app_state.db_pool.close()
```

### 3. Database Connection Pool
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create pool at startup
    pool = await asyncpg.create_pool(
        "postgresql://user:pass@localhost/db",
        min_size=5,
        max_size=20
    )
    app.state.db_pool = pool
    
    yield
    
    # Close pool at shutdown
    await pool.close()
```

### 4. Cache Warming
```python
async def warm_cache():
    """Pre-load frequently accessed data"""
    cache["settings"] = await db.get_settings()
    cache["popular_items"] = await db.get_popular()
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    await warm_cache()  # Load data before accepting requests
    yield
```

### 5. Background Tasks
```python
async def periodic_task():
    while True:
        try:
            await do_something()
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            break

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start task
    task = asyncio.create_task(periodic_task())
    
    yield
    
    # Cancel task
    task.cancel()
    await task
```

### 6. Health & Readiness Probes
```python
@app.get("/health")
def health():
    """Liveness probe - is the app running?"""
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    """Readiness probe - is the app ready for traffic?"""
    if not app_state.is_ready:
        raise HTTPException(503, "Not ready")
    return {"ready": True}
```

---

## Old vs New Approach

### Old (Deprecated)
```python
@app.on_event("startup")
async def startup():
    # Initialize resources
    pass

@app.on_event("shutdown")
async def shutdown():
    # Cleanup resources
    pass
```

### New (Recommended)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)
```

**Why lifespan is better:**
- Clearer resource management
- Works with async context managers
- Resources visible in same function
- Easier testing

---

## Common Patterns

### Pattern 1: Database Pool
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # SQLAlchemy async
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    app.state.engine = engine
    
    yield
    
    await engine.dispose()
```

### Pattern 2: Redis Cache
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await aioredis.from_url("redis://localhost")
    app.state.redis = redis
    
    yield
    
    await redis.close()
```

### Pattern 3: HTTP Client
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Shared HTTP client for external APIs
    client = httpx.AsyncClient()
    app.state.http_client = client
    
    yield
    
    await client.aclose()
```

### Pattern 4: ML Model Loading
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model once at startup
    model = load_model("model.pkl")
    app.state.model = model
    
    yield
    
    # Model cleanup if needed
```

---

## Kubernetes Probes

```yaml
# kubernetes deployment
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Root with status |
| `GET /health` | Health check |
| `GET /ready` | Readiness probe |
| `GET /status` | Detailed status |
| `GET /config` | Configuration |
| `GET /cache` | Cache contents |
| `GET /db/query` | Test DB |

---

## Console Output Example

```
==================================================
🚀 APPLICATION STARTING UP...
==================================================
📝 Loading configuration...
✅ Config loaded: Task Manager API v18.0.0
📊 Creating DB pool (min=5, max=20)
✅ Database pool connected!
🗄️ Connecting to cache...
✅ Cache connected!
🔥 Warming cache with initial data...
✅ Cache warmed with initial data!
⏰ Starting background tasks...
✅ Background tasks started!
==================================================
✅ APPLICATION READY!
⏱️ Startup completed in 1.85s
==================================================
INFO:     Uvicorn running on http://127.0.0.1:8000

# When you stop the server (Ctrl+C):

==================================================
🛑 APPLICATION SHUTTING DOWN...
==================================================
⏰ Cancelling background tasks...
🧹 Cleanup task cancelled
📈 Metrics collector stopped
✅ Background tasks cancelled!
🗄️ Disconnecting cache...
✅ Cache disconnected!
📊 Closing database connections...
✅ Database pool closed!
==================================================
✅ SHUTDOWN COMPLETE (uptime: 0:02:34.567890)
==================================================
```

---

## Exercises

### Exercise 1: Add Redis Connection
- Add simulated Redis connection
- Store session data
- Clean up on shutdown

### Exercise 2: External API Client
- Create shared httpx client
- Use for external API calls
- Close properly on shutdown

### Exercise 3: Graceful Shutdown
- Handle in-flight requests
- Wait for tasks to complete
- Set timeout for shutdown

### Exercise 4: Health Check Details
- Check each resource
- Return degraded status
- Include response times

---

## Best Practices

1. **Initialize expensive resources once** - DB pools, ML models
2. **Clean up properly** - Close connections, cancel tasks
3. **Use health/ready probes** - For load balancers
4. **Handle startup failures** - Fail fast if critical resources unavailable
5. **Log startup/shutdown** - For debugging
6. **Set timeouts** - For startup and shutdown operations

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Startup hangs | Add timeouts to resource initialization |
| Shutdown hangs | Cancel all background tasks |
| Memory leak | Ensure proper cleanup |
| Connection pool exhausted | Configure pool size properly |

---

## What's Next?
**Level 19: OpenAPI Customization** - Customize API documentation and OpenAPI schema.
