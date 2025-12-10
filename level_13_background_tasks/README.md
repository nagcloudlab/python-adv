# Level 13: Background Tasks

## Learning Objectives
- Understand when to use background tasks
- Use `BackgroundTasks` parameter
- Run single and multiple background tasks
- Use async background tasks
- Add background tasks via dependencies
- Handle errors in background tasks
- Create task pipelines
- Know limitations vs task queues

---

## Setup Instructions

```bash
cd level_13_background_tasks
pip install -r requirements.txt
uvicorn main:app --reload
```

**Important:** Watch the console output to see background tasks running!

---

## What are Background Tasks?

Background tasks run **AFTER** the response is sent to the client.

```
┌────────┐      ┌────────┐      ┌────────┐
│ Client │ ──▶  │ Server │ ──▶  │Response│
└────────┘      └────────┘      └────────┘
                     │
                     ▼ (after response sent)
              ┌─────────────┐
              │ Background  │
              │    Task     │
              └─────────────┘
```

**Use Cases:**
- Send email notifications
- Write logs to file/database
- Process uploaded files
- Update search indexes
- Send webhooks
- Cleanup temporary files

---

## Key Concepts

### 1. Basic Background Task
```python
from fastapi import BackgroundTasks

def write_log(message: str):
    # This runs after response is sent
    print(f"Log: {message}")

@app.post("/tasks")
def create_task(title: str, background_tasks: BackgroundTasks):
    # Create task...
    
    # Queue background task
    background_tasks.add_task(write_log, f"Created: {title}")
    
    return {"message": "Created"}  # Returns immediately
```

### 2. Task with Multiple Parameters
```python
def send_email(to: str, subject: str, body: str):
    # Send email...
    pass

@app.post("/notify")
def notify(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        send_email,
        to=email,
        subject="Hello",
        body="World"
    )
    return {"message": "Notification queued"}
```

### 3. Multiple Background Tasks
```python
@app.post("/tasks")
def create_task(background_tasks: BackgroundTasks):
    # Queue multiple tasks
    background_tasks.add_task(write_log, "Task created")
    background_tasks.add_task(update_search_index, task_id)
    background_tasks.add_task(send_notification, user_id)
    background_tasks.add_task(update_analytics, "task_created")
    
    return {"message": "Created with 4 background tasks"}
```

### 4. Async Background Tasks
```python
async def async_process(data: str):
    await asyncio.sleep(2)
    print(f"Processed: {data}")

@app.post("/process")
async def process(background_tasks: BackgroundTasks):
    background_tasks.add_task(async_process, "some data")
    return {"message": "Processing started"}
```

### 5. Background Tasks in Dependencies
```python
def log_dependency(background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, "Request received")
    return background_tasks

@app.get("/items")
def get_items(bg: BackgroundTasks = Depends(log_dependency)):
    return {"items": [...]}
```

### 6. Error Handling
```python
def risky_task(data: str):
    try:
        # Do something risky
        process(data)
    except Exception as e:
        # Log error - don't crash
        logger.error(f"Task failed: {e}")
        # Optional: send alert, retry, etc.

# Note: Background task errors don't affect the response!
```

---

## Background Tasks vs Task Queues

| Feature | BackgroundTasks | Celery/RQ |
|---------|----------------|-----------|
| Setup | Simple | Complex |
| Distribution | Single process | Multiple workers |
| Persistence | None (lost on restart) | Redis/DB backed |
| Retries | Manual | Built-in |
| Monitoring | None | Dashboard |
| Best for | Light tasks | Heavy/critical tasks |

**Use BackgroundTasks for:**
- Quick operations (< 10 seconds)
- Non-critical tasks
- Simple logging/notifications

**Use Celery/RQ for:**
- Long-running tasks
- Critical operations that must complete
- Distributed processing
- Tasks needing retry logic

---

## Task Execution Order

Tasks run **sequentially** in the order added:

```python
background_tasks.add_task(task_a)  # Runs 1st
background_tasks.add_task(task_b)  # Runs 2nd
background_tasks.add_task(task_c)  # Runs 3rd
```

---

## Testing Background Tasks

### Watch Console Output
```bash
uvicorn main:app --reload
# Watch for [Background] log messages
```

### Test Sequence
```bash
# 1. Create task (triggers background log)
curl -X POST "http://localhost:8000/tasks?title=Test"

# 2. Check audit log
curl http://localhost:8000/logs/audit

# 3. Run pipeline
curl -X POST http://localhost:8000/tasks/1/pipeline

# 4. Check pipeline status
curl http://localhost:8000/tasks/1/pipeline/status
```

---

## Common Patterns

### Pattern 1: Email Notification
```python
@app.post("/orders")
def create_order(order: Order, background_tasks: BackgroundTasks):
    # Create order...
    
    background_tasks.add_task(
        send_order_confirmation,
        email=order.customer_email,
        order_id=new_order.id
    )
    
    return {"order_id": new_order.id}
```

### Pattern 2: Audit Logging
```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int, background_tasks: BackgroundTasks):
    # Delete user...
    
    background_tasks.add_task(
        audit_log,
        action="user_deleted",
        user_id=user_id,
        timestamp=datetime.now()
    )
    
    return {"message": "Deleted"}
```

### Pattern 3: File Processing
```python
@app.post("/upload")
def upload(file: UploadFile, background_tasks: BackgroundTasks):
    # Save file...
    
    background_tasks.add_task(
        process_and_cleanup,
        file_path=saved_path
    )
    
    return {"status": "Processing started"}
```

### Pattern 4: Webhook Delivery
```python
@app.post("/events")
def create_event(event: Event, background_tasks: BackgroundTasks):
    # Create event...
    
    for webhook_url in subscriber_webhooks:
        background_tasks.add_task(
            deliver_webhook,
            url=webhook_url,
            payload=event.dict()
        )
    
    return {"event_id": event.id}
```

---

## Exercises

### Exercise 1: Welcome Email
Create endpoint that:
- Registers a new user
- Sends welcome email in background
- Logs registration to audit log

### Exercise 2: Report Generator
Create endpoint that:
- Accepts report parameters
- Returns job ID immediately
- Generates report in background
- Sends email when complete

### Exercise 3: Image Processing
Create endpoint that:
- Accepts image upload
- Returns immediately
- Processes image in background (resize, optimize)
- Updates database when done

### Exercise 4: Retry Logic
Create background task that:
- Attempts operation up to 3 times
- Waits between retries
- Logs final result (success/failure)

---

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| Expecting task result in response | Tasks run AFTER response |
| No error handling | Wrap in try/except |
| Very long tasks | Use Celery instead |
| Assuming task completed | Check status separately |

---

## Best Practices

1. **Keep tasks short** - Under 10 seconds ideally
2. **Always handle errors** - Log failures, don't crash
3. **Don't return task results** - Response is already sent
4. **Use for non-critical operations** - Email, logging, etc.
5. **Consider task queues** - For heavy/critical work
6. **Log task execution** - For debugging

---

## What's Next?
**Level 14: APIRouter & Project Structure** - Learn to organize large APIs with routers, multiple files, and proper project structure.
