"""
Level 13: Background Tasks
==========================
Concepts Covered:
    - What are background tasks
    - BackgroundTasks parameter
    - Single background task
    - Multiple background tasks
    - Background tasks with parameters
    - Common use cases (email, logging, cleanup)
    - Limitations vs task queues (Celery)

Run Command:
    uvicorn main:app --reload

Test:
    http://127.0.0.1:8000/docs
    Watch console for background task output
"""

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import time
import asyncio
import logging

# Configure logging to see background task output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Task Manager API - Level 13",
    description="Learning Background Tasks",
    version="13.0.0"
)


# ============================================================
# CONCEPT 1: What are Background Tasks?
# ============================================================
"""
Background Tasks run AFTER the response is sent to the client.

Use cases:
- Send email notifications
- Write logs to file/database
- Process uploaded files
- Cleanup temporary files
- Update caches
- Send webhooks

Benefits:
- Client gets immediate response
- Long operations don't block the response
- Simple to use (no external queue needed)

Limitations:
- Runs in the same process (not distributed)
- Lost if server restarts
- Not suitable for very long tasks
- For heavy tasks, use Celery/RQ/etc.
"""


# ============================================================
# Sample Data
# ============================================================

tasks_db = {}
notifications_log = []
audit_log = []


# ============================================================
# CONCEPT 2: Basic Background Task
# ============================================================

def write_log(message: str):
    """
    Simple background task - writes to log
    
    This runs AFTER response is sent
    """
    logger.info(f"[Background] Writing log: {message}")
    time.sleep(1)  # Simulate slow operation
    audit_log.append({
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    logger.info(f"[Background] Log written successfully")


@app.post("/tasks")
def create_task(
    title: str,
    background_tasks: BackgroundTasks
):
    """
    Create task with background logging
    
    1. Response sent immediately
    2. Log is written in background
    
    Watch console for background task output!
    """
    # Create task
    task_id = len(tasks_db) + 1
    task = {
        "id": task_id,
        "title": title,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    tasks_db[task_id] = task
    
    # Add background task (runs after response)
    background_tasks.add_task(write_log, f"Task created: {title}")
    
    return {
        "message": "Task created (logging in background)",
        "task": task
    }


# ============================================================
# CONCEPT 3: Background Task with Multiple Parameters
# ============================================================

def send_email_notification(
    email: str,
    subject: str,
    body: str,
    task_id: int
):
    """
    Simulate sending email (background task)
    """
    logger.info(f"[Background] Sending email to {email}...")
    time.sleep(2)  # Simulate email sending delay
    
    notifications_log.append({
        "type": "email",
        "to": email,
        "subject": subject,
        "task_id": task_id,
        "sent_at": datetime.now().isoformat()
    })
    
    logger.info(f"[Background] Email sent to {email}")


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_email: Optional[EmailStr] = None


@app.post("/tasks/with-notification")
def create_task_with_notification(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks
):
    """
    Create task and send email notification in background
    
    Response returns immediately, email sends in background
    """
    # Create task
    task_id = len(tasks_db) + 1
    task = {
        "id": task_id,
        "title": task_data.title,
        "description": task_data.description,
        "assignee": task_data.assignee_email,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    tasks_db[task_id] = task
    
    # Send notification if assignee provided
    if task_data.assignee_email:
        background_tasks.add_task(
            send_email_notification,
            email=task_data.assignee_email,
            subject=f"New Task Assigned: {task_data.title}",
            body=f"You have been assigned a new task: {task_data.title}",
            task_id=task_id
        )
    
    # Log the creation
    background_tasks.add_task(
        write_log,
        f"Task {task_id} created and assigned to {task_data.assignee_email}"
    )
    
    return {
        "message": "Task created (notification sending in background)",
        "task": task
    }


# ============================================================
# CONCEPT 4: Multiple Background Tasks
# ============================================================

def update_search_index(task_id: int, title: str):
    """Simulate updating search index"""
    logger.info(f"[Background] Updating search index for task {task_id}...")
    time.sleep(1)
    logger.info(f"[Background] Search index updated")


def notify_webhook(url: str, data: dict):
    """Simulate sending webhook"""
    logger.info(f"[Background] Sending webhook to {url}...")
    time.sleep(1)
    logger.info(f"[Background] Webhook sent")


def update_analytics(event: str, metadata: dict):
    """Simulate updating analytics"""
    logger.info(f"[Background] Recording analytics: {event}...")
    time.sleep(0.5)
    logger.info(f"[Background] Analytics recorded")


@app.post("/tasks/full")
def create_task_full(
    title: str,
    background_tasks: BackgroundTasks,
    notify_url: Optional[str] = None
):
    """
    Create task with multiple background operations
    
    All these run in background after response:
    1. Write audit log
    2. Update search index
    3. Send webhook (if URL provided)
    4. Update analytics
    """
    task_id = len(tasks_db) + 1
    task = {
        "id": task_id,
        "title": title,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    tasks_db[task_id] = task
    
    # Queue multiple background tasks
    background_tasks.add_task(write_log, f"Task {task_id} created")
    background_tasks.add_task(update_search_index, task_id, title)
    background_tasks.add_task(update_analytics, "task_created", {"task_id": task_id})
    
    if notify_url:
        background_tasks.add_task(notify_webhook, notify_url, {"task": task})
    
    return {
        "message": "Task created (4 background tasks queued)",
        "task": task,
        "background_tasks_queued": [
            "write_log",
            "update_search_index",
            "update_analytics",
            "notify_webhook" if notify_url else None
        ]
    }


# ============================================================
# CONCEPT 5: Async Background Tasks
# ============================================================

async def async_process_file(filename: str, task_id: int):
    """
    Async background task - can use await
    """
    logger.info(f"[Background] Processing file: {filename}...")
    
    # Simulate async file processing
    await asyncio.sleep(2)
    
    logger.info(f"[Background] File processed: {filename}")
    
    # Update task
    if task_id in tasks_db:
        tasks_db[task_id]["file_processed"] = True


@app.post("/tasks/{task_id}/upload")
async def upload_file(
    task_id: int,
    filename: str,
    background_tasks: BackgroundTasks
):
    """
    Upload file with async background processing
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Queue async background task
    background_tasks.add_task(async_process_file, filename, task_id)
    
    return {
        "message": f"File {filename} uploaded, processing in background",
        "task_id": task_id
    }


# ============================================================
# CONCEPT 6: Background Task for Cleanup
# ============================================================

temp_files = []


def cleanup_temp_files(file_ids: List[int]):
    """
    Background task to cleanup temporary files
    """
    logger.info(f"[Background] Cleaning up {len(file_ids)} temp files...")
    time.sleep(1)
    
    for file_id in file_ids:
        if file_id in temp_files:
            temp_files.remove(file_id)
            logger.info(f"[Background] Removed temp file: {file_id}")
    
    logger.info(f"[Background] Cleanup complete")


@app.post("/export")
def export_data(
    background_tasks: BackgroundTasks,
    format: str = "csv"
):
    """
    Export data - creates temp file, schedules cleanup
    """
    # Create temp file
    temp_file_id = len(temp_files) + 1
    temp_files.append(temp_file_id)
    
    # Schedule cleanup after response
    background_tasks.add_task(cleanup_temp_files, [temp_file_id])
    
    return {
        "message": "Export started",
        "temp_file_id": temp_file_id,
        "format": format,
        "note": "Temp file will be cleaned up in background"
    }


# ============================================================
# CONCEPT 7: Background Task with Error Handling
# ============================================================

def risky_background_task(task_id: int, should_fail: bool = False):
    """
    Background task that might fail
    
    Note: Errors in background tasks don't affect the response!
    """
    logger.info(f"[Background] Starting risky task for {task_id}...")
    
    try:
        if should_fail:
            raise ValueError("Simulated error!")
        
        time.sleep(1)
        logger.info(f"[Background] Risky task completed successfully")
        
    except Exception as e:
        # Log error but don't crash
        logger.error(f"[Background] Task failed: {e}")
        # In real app: send alert, retry, etc.


@app.post("/tasks/{task_id}/process")
def process_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    simulate_error: bool = False
):
    """
    Process task in background (may fail)
    
    Set simulate_error=true to see error handling
    Response is still successful even if background task fails!
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    background_tasks.add_task(risky_background_task, task_id, simulate_error)
    
    return {
        "message": "Processing started in background",
        "task_id": task_id,
        "note": "Check console for background task output"
    }


# ============================================================
# CONCEPT 8: Chained Background Tasks
# ============================================================

def step_one(task_id: int, results: dict):
    """First step of processing"""
    logger.info(f"[Background] Step 1 starting for task {task_id}...")
    time.sleep(1)
    results["step_one"] = "completed"
    logger.info(f"[Background] Step 1 completed")


def step_two(task_id: int, results: dict):
    """Second step - runs after step one"""
    logger.info(f"[Background] Step 2 starting for task {task_id}...")
    time.sleep(1)
    results["step_two"] = "completed"
    logger.info(f"[Background] Step 2 completed")


def step_three(task_id: int, results: dict):
    """Final step"""
    logger.info(f"[Background] Step 3 starting for task {task_id}...")
    time.sleep(1)
    results["step_three"] = "completed"
    
    # Update task with results
    if task_id in tasks_db:
        tasks_db[task_id]["processing_results"] = results
    
    logger.info(f"[Background] All steps completed: {results}")


processing_results = {}


@app.post("/tasks/{task_id}/pipeline")
def run_pipeline(
    task_id: int,
    background_tasks: BackgroundTasks
):
    """
    Run multi-step pipeline in background
    
    Tasks run in order: step_one → step_two → step_three
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Shared results dict
    results = {"task_id": task_id, "started_at": datetime.now().isoformat()}
    processing_results[task_id] = results
    
    # Add tasks in order (they run sequentially)
    background_tasks.add_task(step_one, task_id, results)
    background_tasks.add_task(step_two, task_id, results)
    background_tasks.add_task(step_three, task_id, results)
    
    return {
        "message": "Pipeline started",
        "task_id": task_id,
        "steps": ["step_one", "step_two", "step_three"]
    }


@app.get("/tasks/{task_id}/pipeline/status")
def get_pipeline_status(task_id: int):
    """Check pipeline processing status"""
    if task_id not in processing_results:
        return {"status": "not_started"}
    
    return {
        "status": "processing",
        "results": processing_results[task_id]
    }


# ============================================================
# List Tasks Endpoint
# ============================================================

@app.get("/tasks")
def list_tasks(background_tasks: BackgroundTasks):
    """
    List all tasks - logs access in background
    """
    # Add logging as background task
    background_tasks.add_task(
        write_log,
        f"Tasks listed at {datetime.now().isoformat()}"
    )
    
    return {
        "total": len(tasks_db),
        "tasks": list(tasks_db.values())
    }


# ============================================================
# Utility Endpoints
# ============================================================

@app.get("/logs/audit")
def get_audit_log():
    """View audit log (populated by background tasks)"""
    return {"audit_log": audit_log}


@app.get("/logs/notifications")
def get_notifications():
    """View notification log"""
    return {"notifications": notifications_log}


@app.delete("/logs")
def clear_logs(background_tasks: BackgroundTasks):
    """Clear all logs"""
    audit_log.clear()
    notifications_log.clear()
    background_tasks.add_task(write_log, "Logs cleared")
    return {"message": "Logs cleared"}


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """API Root"""
    return {
        "message": "Level 13 - Background Tasks",
        "concepts": [
            "BackgroundTasks parameter",
            "Single background task",
            "Multiple background tasks",
            "Async background tasks",
            "Error handling in background tasks",
            "Chained/pipeline tasks"
        ],
        "test_flow": [
            "1. POST /tasks?title=Test - Create task (watch console)",
            "2. POST /tasks/with-notification - With email",
            "3. POST /tasks/full - Multiple background tasks",
            "4. POST /tasks/{id}/pipeline - Multi-step pipeline",
            "5. GET /logs/audit - See background task results"
        ],
        "important": "Watch the console to see background task execution!"
    }
