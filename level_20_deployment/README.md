# Level 20: Deployment 🚀

## Learning Objectives
- Configure production settings
- Use environment variables
- Run with Gunicorn + Uvicorn workers
- Build Docker images
- Use Docker Compose
- Implement health checks
- Configure logging
- Apply security best practices

---

## Project Structure

```
level_20_deployment/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── Dockerfile               # Container image
├── docker-compose.yml       # Multi-container setup
├── gunicorn.conf.py        # Gunicorn configuration
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── .dockerignore           # Docker ignore rules
└── README.md               # This file
```

---

## Quick Start

### Option 1: Local Development
```bash
cd level_20_deployment
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Option 2: Gunicorn (Production-like)
```bash
pip install -r requirements.txt
gunicorn app.main:app -c gunicorn.conf.py
```

### Option 3: Docker
```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

### Option 4: Docker Compose
```bash
docker-compose up -d
```

---

## Key Concepts

### 1. Environment Variables
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "My API"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Gunicorn with Uvicorn Workers
```bash
# Run with Gunicorn
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### 3. Dockerfile (Multi-stage)
```dockerfile
# Build stage
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install -r requirements.txt

# Production stage
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app
WORKDIR /app
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### 4. Health Checks
```python
@app.get("/health")
def health():
    """Liveness probe"""
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    """Readiness probe"""
    if not app_ready:
        raise HTTPException(503)
    return {"status": "ready"}
```

### 5. Docker Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

---

## Deployment Checklist

### Security
- [ ] Change SECRET_KEY
- [ ] Disable DEBUG in production
- [ ] Configure CORS properly
- [ ] Use HTTPS
- [ ] Run as non-root user
- [ ] Hide docs in production

### Performance
- [ ] Set appropriate worker count
- [ ] Configure timeouts
- [ ] Enable connection pooling
- [ ] Set up caching

### Monitoring
- [ ] Configure logging
- [ ] Set up health checks
- [ ] Add metrics endpoint
- [ ] Configure error tracking (Sentry)

### Infrastructure
- [ ] Use environment variables
- [ ] Set up CI/CD
- [ ] Configure load balancer
- [ ] Set up database backups

---

## Worker Count Formula

```python
workers = (2 * cpu_cores) + 1
```

| CPU Cores | Workers |
|-----------|---------|
| 1 | 3 |
| 2 | 5 |
| 4 | 9 |
| 8 | 17 |

---

## Docker Commands

```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -d -p 8000:8000 --name api fastapi-app

# View logs
docker logs -f api

# Stop container
docker stop api

# Remove container
docker rm api

# Docker Compose
docker-compose up -d      # Start all services
docker-compose down       # Stop all services
docker-compose logs -f    # View logs
docker-compose ps         # List services
```

---

## Environment Configuration

### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Staging
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
```

### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

---

## Health Check URLs

| Endpoint | Purpose |
|----------|---------|
| `/health` | Liveness probe |
| `/ready` | Readiness probe |
| `/metrics` | Basic metrics |

---

## Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Change PORT or stop other service |
| Permission denied | Run as root or fix file permissions |
| Module not found | Check PYTHONPATH and working directory |
| Database connection failed | Check DATABASE_URL and network |
| Workers dying | Increase timeout or memory |

---

## Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use multi-stage builds** - Smaller images
3. **Run as non-root** - Security
4. **Health checks** - For orchestration
5. **Graceful shutdown** - Handle SIGTERM
6. **Structured logging** - JSON format for production
7. **Connection pooling** - Database efficiency
8. **Rate limiting** - Protect from abuse

---

## Congratulations! 🎉

You've completed all 20 levels of FastAPI training!

### Summary of Topics Covered

| Level | Topic |
|-------|-------|
| 1-3 | Basics, Path & Query Parameters |
| 4-6 | Request Body, Response Models, Forms & Files |
| 7-9 | Validation, Headers/Cookies, Status Codes |
| 10-11 | Dependency Injection, Security |
| 12-13 | Middleware, Background Tasks |
| 14-15 | Project Structure, Database (SQLAlchemy) |
| 16-17 | Testing, WebSockets |
| 18-19 | Lifespan Events, OpenAPI Customization |
| 20 | **Deployment** |

### Next Steps

1. Build a complete project
2. Add more features (caching, rate limiting)
3. Set up CI/CD pipeline
4. Deploy to cloud (AWS, GCP, Azure)
5. Add monitoring (Prometheus, Grafana)
6. Implement advanced patterns (CQRS, Event Sourcing)

**Happy coding!** 🐍🚀
