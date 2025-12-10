"""
Gunicorn Configuration for Production
======================================
Run: gunicorn app.main:app -c gunicorn.conf.py

Gunicorn is a production WSGI server.
We use uvicorn workers to run FastAPI (ASGI).
"""

import os
import multiprocessing

# ============================================================
# Server Socket
# ============================================================

# Bind address
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}"

# Backlog - number of pending connections
backlog = 2048


# ============================================================
# Worker Processes
# ============================================================

# Worker class - use uvicorn for ASGI
worker_class = "uvicorn.workers.UvicornWorker"

# Number of workers
# Rule of thumb: (2 x CPU cores) + 1
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Threads per worker (for sync workers, not used with uvicorn)
threads = 1

# Maximum requests per worker before restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50  # Random jitter to prevent all workers restarting at once


# ============================================================
# Timeouts
# ============================================================

# Worker timeout (seconds)
timeout = 30

# Graceful timeout for workers to finish requests
graceful_timeout = 30

# Keep-alive timeout
keepalive = 5


# ============================================================
# Server Mechanics
# ============================================================

# Daemonize the process (run in background)
daemon = False

# PID file
pidfile = None  # "/var/run/gunicorn.pid" for production

# User and group to run as
user = None   # "appuser" for production
group = None  # "appgroup" for production

# Working directory
chdir = os.path.dirname(os.path.abspath(__file__))

# Umask for file creation
umask = 0

# Temporary file directory
tmp_upload_dir = None


# ============================================================
# Logging
# ============================================================

# Access log
accesslog = "-"  # "-" means stdout, or "/var/log/gunicorn/access.log"

# Error log
errorlog = "-"   # "-" means stderr, or "/var/log/gunicorn/error.log"

# Log level
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Capture stdout/stderr from workers
capture_output = True

# Enable access log
enable_stdio_inheritance = True


# ============================================================
# Process Naming
# ============================================================

proc_name = os.getenv("APP_NAME", "fastapi-app")


# ============================================================
# Server Hooks
# ============================================================

def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 50)
    print("Starting Gunicorn server...")
    print(f"Workers: {workers}")
    print(f"Bind: {bind}")
    print("=" * 50)


def on_reload(server):
    """Called before reloading the configuration."""
    print("Reloading configuration...")


def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    print(f"Worker {worker.pid} interrupted")


def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    print(f"Worker {worker.pid} aborted")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"Worker {worker.pid} spawned")


def post_worker_init(worker):
    """Called just after a worker has initialized."""
    pass


def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"Worker {worker.pid} exited")


def nworkers_changed(server, new_value, old_value):
    """Called when the number of workers changes."""
    print(f"Workers changed from {old_value} to {new_value}")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("Shutting down Gunicorn server...")


# ============================================================
# SSL/TLS (Optional)
# ============================================================

# SSL certificate file
# certfile = "/path/to/cert.pem"

# SSL key file
# keyfile = "/path/to/key.pem"

# SSL version
# ssl_version = "TLS"

# CA certificates file
# ca_certs = "/path/to/ca-bundle.crt"

# Whether to require client certificate
# cert_reqs = 0  # 0=no, 1=optional, 2=required
