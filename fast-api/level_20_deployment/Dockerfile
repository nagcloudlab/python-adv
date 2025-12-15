# ============================================================
# Level 20: Production Dockerfile
# ============================================================
# Multi-stage build for smaller image size

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# Stage 2: Production stage
FROM python:3.11-slim as production

# Labels
LABEL maintainer="your-email@example.com"
LABEL version="20.0.0"
LABEL description="Production FastAPI application"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # App settings
    APP_NAME="Task Manager API" \
    ENVIRONMENT=production \
    DEBUG=false \
    HOST=0.0.0.0 \
    PORT=8000 \
    WORKERS=4

# Create non-root user for security
RUN groupadd -r appgroup && \
    useradd -r -g appgroup appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run with Gunicorn
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
