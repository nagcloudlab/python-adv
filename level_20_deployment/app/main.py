"""
Level 20: Deployment
====================
Production-ready FastAPI application with Docker and Gunicorn.

Concepts Covered:
    - Production configuration
    - Environment variables
    - Gunicorn with Uvicorn workers
    - Docker containerization
    - Docker Compose
    - Health checks
    - Logging configuration
    - CORS configuration
    - Security headers
    - Graceful shutdown

Run Locally:
    uvicorn app.main:app --reload

Run with Gunicorn:
    gunicorn app.main:app -c gunicorn.conf.py

Run with Docker:
    docker build -t fastapi-app .
    docker run -p 8000:8000 fastapi-app

Run with Docker Compose:
    docker-compose up
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings
from typing import List, Optional
from datetime import datetime
import logging
import os


# ============================================================
# CONCEPT 1: Production Settings with Environment Variables
# ============================================================

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    In production, set these via:
    - Environment variables
    - .env file
    - Docker environment
    - Kubernetes ConfigMaps/Secrets
    """
    
    # Application
    APP_NAME: str = "Task Manager API"
    APP_VERSION: str = "20.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    API_KEY: str = "change-me-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Database (example)
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Redis (example)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Load settings
settings = Settings()


# ============================================================
# CONCEPT 2: Logging Configuration
# ============================================================

def setup_logging():
    """Configure logging for production"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),  # Console output
            # Add file handler in production:
            # logging.FileHandler("/var/log/app/app.log")
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================
# CONCEPT 3: Application State
# ============================================================

class AppState:
    """Application state for shared resources"""
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.request_count: int = 0
        self.is_ready: bool = False


app_state = AppState()


# ============================================================
# CONCEPT 4: Lifespan for Startup/Shutdown
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info("=" * 50)
    
    app_state.start_time = datetime.now()
    
    # Initialize resources here (database, cache, etc.)
    # await database.connect()
    # await cache.connect()
    
    app_state.is_ready = True
    logger.info("Application ready to accept requests")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Cleanup resources
    # await database.disconnect()
    # await cache.disconnect()
    
    app_state.is_ready = False
    logger.info("Application shutdown complete")


# ============================================================
# CONCEPT 5: Create FastAPI Application
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready FastAPI application",
    docs_url="/docs" if settings.DEBUG else None,  # Disable in production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)


# ============================================================
# CONCEPT 6: CORS Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CONCEPT 7: Security Headers Middleware
# ============================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# ============================================================
# CONCEPT 8: Request Counting Middleware
# ============================================================

@app.middleware("http")
async def count_requests(request: Request, call_next):
    """Count requests for metrics"""
    app_state.request_count += 1
    response = await call_next(request)
    return response


# ============================================================
# CONCEPT 9: Health Check Endpoints
# ============================================================

@app.get("/health", tags=["Health"])
def health_check():
    """
    Liveness probe - is the application running?
    
    Used by:
    - Docker HEALTHCHECK
    - Kubernetes livenessProbe
    - Load balancers
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/ready", tags=["Health"])
def readiness_check():
    """
    Readiness probe - is the application ready for traffic?
    
    Used by:
    - Kubernetes readinessProbe
    - Load balancers
    """
    if not app_state.is_ready:
        raise HTTPException(status_code=503, detail="Not ready")
    
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics", tags=["Health"])
def metrics():
    """
    Basic metrics endpoint
    
    In production, use Prometheus metrics
    """
    uptime = datetime.now() - app_state.start_time if app_state.start_time else None
    
    return {
        "uptime_seconds": uptime.total_seconds() if uptime else 0,
        "request_count": app_state.request_count,
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION
    }


# ============================================================
# CONCEPT 10: Application Endpoints
# ============================================================

# Sample data
tasks = {
    1: {"id": 1, "title": "Deploy to production", "status": "pending"},
    2: {"id": 2, "title": "Setup monitoring", "status": "pending"},
}


@app.get("/", tags=["Root"])
def root():
    """API root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "Disabled in production"
    }


@app.get("/tasks", tags=["Tasks"])
def list_tasks():
    """List all tasks"""
    logger.info("Listing all tasks")
    return {"tasks": list(tasks.values())}


@app.get("/tasks/{task_id}", tags=["Tasks"])
def get_task(task_id: int):
    """Get task by ID"""
    if task_id not in tasks:
        logger.warning(f"Task {task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.post("/tasks", tags=["Tasks"])
def create_task(title: str):
    """Create a new task"""
    task_id = max(tasks.keys()) + 1 if tasks else 1
    task = {"id": task_id, "title": title, "status": "pending"}
    tasks[task_id] = task
    logger.info(f"Created task {task_id}: {title}")
    return task


# ============================================================
# CONCEPT 11: Error Handling
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)}
        )


# ============================================================
# Info endpoint
# ============================================================

@app.get("/info", tags=["Root"])
def info():
    """Deployment information"""
    return {
        "message": "Level 20 - Deployment",
        "concepts": [
            "Environment variables",
            "Production settings",
            "Gunicorn configuration",
            "Docker containerization",
            "Docker Compose",
            "Health checks",
            "Security headers",
            "Logging configuration",
            "CORS configuration",
            "Graceful shutdown"
        ],
        "files": {
            "Dockerfile": "Container image",
            "docker-compose.yml": "Multi-container setup",
            "gunicorn.conf.py": "Gunicorn configuration",
            ".env.example": "Environment template"
        }
    }
