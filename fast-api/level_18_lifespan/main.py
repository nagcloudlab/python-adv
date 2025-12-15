"""
Level 18: Lifespan Events
=========================
Learn application startup and shutdown events for resource management.

Concepts Covered:
    - Lifespan context manager (modern approach)
    - Startup events (deprecated but shown for reference)
    - Shutdown events (deprecated but shown for reference)
    - Database connection initialization
    - Cache warming
    - Background task schedulers
    - Cleanup on shutdown
    - Shared application state

Run Command:
    uvicorn main:app --reload

Watch the console for startup/shutdown messages!
"""

from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# CONCEPT 1: Application State (Shared Resources)
# ============================================================

class AppState:
    """
    Container for application-wide shared state
    
    This holds resources that:
    - Are initialized at startup
    - Shared across all requests
    - Cleaned up at shutdown
    """
    
    def __init__(self):
        self.db_pool: Optional[Any] = None
        self.cache: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
        self.startup_time: Optional[datetime] = None
        self.background_tasks: List[asyncio.Task] = []
        self.is_ready: bool = False


# Global app state
app_state = AppState()


# ============================================================
# CONCEPT 2: Simulated Resources
# ============================================================

class FakeDBPool:
    """Simulated database connection pool"""
    
    def __init__(self, min_size: int = 5, max_size: int = 20):
        self.min_size = min_size
        self.max_size = max_size
        self.connections = []
        self._connected = False
    
    async def connect(self):
        """Initialize connection pool"""
        logger.info(f"📊 Creating DB pool (min={self.min_size}, max={self.max_size})")
        await asyncio.sleep(0.5)  # Simulate connection time
        self._connected = True
        logger.info("✅ Database pool connected!")
    
    async def disconnect(self):
        """Close all connections"""
        logger.info("📊 Closing database connections...")
        await asyncio.sleep(0.3)  # Simulate cleanup
        self._connected = False
        logger.info("✅ Database pool closed!")
    
    def is_connected(self) -> bool:
        return self._connected
    
    async def execute(self, query: str):
        """Simulate query execution"""
        if not self._connected:
            raise RuntimeError("Database not connected!")
        await asyncio.sleep(0.1)
        return {"query": query, "result": "success"}


class FakeCache:
    """Simulated cache (like Redis)"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self._connected = False
    
    async def connect(self):
        logger.info("🗄️ Connecting to cache...")
        await asyncio.sleep(0.3)
        self._connected = True
        logger.info("✅ Cache connected!")
    
    async def disconnect(self):
        logger.info("🗄️ Disconnecting cache...")
        await asyncio.sleep(0.2)
        self._connected = False
        logger.info("✅ Cache disconnected!")
    
    async def warm_cache(self):
        """Pre-load frequently accessed data"""
        logger.info("🔥 Warming cache with initial data...")
        await asyncio.sleep(0.5)
        self.data = {
            "settings": {"theme": "dark", "language": "en"},
            "popular_items": [1, 2, 3, 4, 5],
            "feature_flags": {"new_ui": True, "beta_features": False}
        }
        logger.info("✅ Cache warmed with initial data!")
    
    def get(self, key: str) -> Optional[Any]:
        return self.data.get(key)
    
    def set(self, key: str, value: Any):
        self.data[key] = value


# ============================================================
# CONCEPT 3: Background Task
# ============================================================

async def periodic_cleanup_task():
    """
    Background task that runs periodically
    
    In real apps, this could:
    - Clean expired sessions
    - Refresh tokens
    - Update statistics
    - Health checks
    """
    while True:
        try:
            logger.info("🧹 Running periodic cleanup...")
            await asyncio.sleep(60)  # Run every 60 seconds
        except asyncio.CancelledError:
            logger.info("🧹 Cleanup task cancelled")
            break


async def metrics_collector_task():
    """Collect and log metrics periodically"""
    while True:
        try:
            logger.info("📈 Collecting metrics...")
            # Simulate metrics collection
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info("📈 Metrics collector stopped")
            break


# ============================================================
# CONCEPT 4: Lifespan Context Manager (Modern Approach)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    
    This is the MODERN way to handle startup/shutdown.
    
    Code BEFORE yield = startup
    Code AFTER yield = shutdown
    
    Benefits:
    - Clean, explicit resource management
    - Works with async context managers
    - Type-safe
    - No global state pollution
    """
    
    # ========== STARTUP ==========
    logger.info("=" * 50)
    logger.info("🚀 APPLICATION STARTING UP...")
    logger.info("=" * 50)
    
    # Record startup time
    app_state.startup_time = datetime.now()
    
    # 1. Load configuration
    logger.info("📝 Loading configuration...")
    app_state.config = {
        "app_name": "Task Manager API",
        "version": "18.0.0",
        "environment": "development",
        "debug": True
    }
    logger.info(f"✅ Config loaded: {app_state.config['app_name']} v{app_state.config['version']}")
    
    # 2. Initialize database pool
    db_pool = FakeDBPool(min_size=5, max_size=20)
    await db_pool.connect()
    app_state.db_pool = db_pool
    
    # 3. Initialize cache
    cache = FakeCache()
    await cache.connect()
    await cache.warm_cache()
    app_state.cache = cache.data
    
    # 4. Start background tasks
    logger.info("⏰ Starting background tasks...")
    cleanup_task = asyncio.create_task(periodic_cleanup_task())
    metrics_task = asyncio.create_task(metrics_collector_task())
    app_state.background_tasks = [cleanup_task, metrics_task]
    logger.info("✅ Background tasks started!")
    
    # 5. Mark as ready
    app_state.is_ready = True
    
    logger.info("=" * 50)
    logger.info("✅ APPLICATION READY!")
    logger.info(f"⏱️ Startup completed in {(datetime.now() - app_state.startup_time).total_seconds():.2f}s")
    logger.info("=" * 50)
    
    # ========== YIELD (App runs here) ==========
    yield
    
    # ========== SHUTDOWN ==========
    logger.info("=" * 50)
    logger.info("🛑 APPLICATION SHUTTING DOWN...")
    logger.info("=" * 50)
    
    # 1. Cancel background tasks
    logger.info("⏰ Cancelling background tasks...")
    for task in app_state.background_tasks:
        task.cancel()
    await asyncio.gather(*app_state.background_tasks, return_exceptions=True)
    logger.info("✅ Background tasks cancelled!")
    
    # 2. Close cache
    cache = FakeCache()  # Get reference
    await cache.disconnect()
    
    # 3. Close database
    await app_state.db_pool.disconnect()
    
    # 4. Final cleanup
    app_state.is_ready = False
    
    uptime = datetime.now() - app_state.startup_time
    logger.info("=" * 50)
    logger.info(f"✅ SHUTDOWN COMPLETE (uptime: {uptime})")
    logger.info("=" * 50)


# ============================================================
# Create FastAPI App with Lifespan
# ============================================================

app = FastAPI(
    title="Task Manager API - Level 18",
    description="Learning Lifespan Events",
    version="18.0.0",
    lifespan=lifespan  # Attach lifespan handler
)


# ============================================================
# CONCEPT 5: Dependency that uses App State
# ============================================================

def get_db():
    """
    Dependency to get database connection
    
    Uses the pool initialized at startup
    """
    if not app_state.db_pool or not app_state.db_pool.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )
    return app_state.db_pool


def get_cache():
    """Dependency to get cache"""
    return app_state.cache


def require_ready():
    """Dependency that ensures app is fully initialized"""
    if not app_state.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Application not ready"
        )
    return True


# ============================================================
# Endpoints
# ============================================================

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Level 18 - Lifespan Events",
        "status": "ready" if app_state.is_ready else "starting",
        "startup_time": app_state.startup_time.isoformat() if app_state.startup_time else None
    }


@app.get("/health")
def health():
    """
    Health check endpoint
    
    Checks if all resources are ready
    """
    db_ready = app_state.db_pool and app_state.db_pool.is_connected()
    
    return {
        "status": "healthy" if app_state.is_ready else "unhealthy",
        "checks": {
            "database": "connected" if db_ready else "disconnected",
            "cache": "loaded" if app_state.cache else "empty",
            "background_tasks": len(app_state.background_tasks)
        },
        "uptime_seconds": (datetime.now() - app_state.startup_time).total_seconds() if app_state.startup_time else 0
    }


@app.get("/ready")
def readiness(ready: bool = Depends(require_ready)):
    """
    Readiness probe for Kubernetes/load balancers
    
    Returns 200 only when app is fully ready
    """
    return {"ready": True}


@app.get("/config")
def get_config():
    """Get application configuration"""
    return {
        "config": app_state.config,
        "startup_time": app_state.startup_time.isoformat() if app_state.startup_time else None
    }


@app.get("/cache")
def view_cache(cache: dict = Depends(get_cache)):
    """View cached data"""
    return {"cache": cache}


@app.get("/cache/{key}")
def get_cache_item(key: str, cache: dict = Depends(get_cache)):
    """Get specific cache item"""
    if key not in cache:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not in cache")
    return {"key": key, "value": cache[key]}


@app.get("/db/query")
async def test_db_query(
    db: FakeDBPool = Depends(get_db),
    ready: bool = Depends(require_ready)
):
    """
    Test database query
    
    Uses the database pool initialized at startup
    """
    result = await db.execute("SELECT * FROM tasks")
    return {"result": result}


@app.get("/status")
def status():
    """Detailed application status"""
    return {
        "app": app_state.config.get("app_name", "Unknown"),
        "version": app_state.config.get("version", "Unknown"),
        "environment": app_state.config.get("environment", "Unknown"),
        "is_ready": app_state.is_ready,
        "startup_time": app_state.startup_time.isoformat() if app_state.startup_time else None,
        "uptime": str(datetime.now() - app_state.startup_time) if app_state.startup_time else None,
        "resources": {
            "database": "connected" if app_state.db_pool and app_state.db_pool.is_connected() else "disconnected",
            "cache_items": len(app_state.cache) if app_state.cache else 0,
            "background_tasks": len(app_state.background_tasks)
        }
    }


@app.get("/info")
def info():
    """API Information"""
    return {
        "message": "Level 18 - Lifespan Events",
        "concepts": [
            "Lifespan context manager (@asynccontextmanager)",
            "Startup initialization",
            "Shutdown cleanup",
            "Database pool management",
            "Cache warming",
            "Background tasks",
            "Health/readiness probes",
            "Application state"
        ],
        "watch": "Console logs for startup/shutdown messages",
        "endpoints": {
            "/health": "Health check",
            "/ready": "Readiness probe",
            "/status": "Detailed status",
            "/config": "Configuration",
            "/cache": "Cache contents",
            "/db/query": "Test DB connection"
        }
    }


# ============================================================
# CONCEPT 6: Deprecated Approach (for reference)
# ============================================================

"""
The OLD way (deprecated in FastAPI 0.93+):

@app.on_event("startup")
async def startup_event():
    # Initialize resources
    pass

@app.on_event("shutdown")  
async def shutdown_event():
    # Cleanup resources
    pass

This still works but lifespan is preferred because:
1. Clearer resource management
2. Better for async context managers
3. More Pythonic
4. Easier testing
"""
