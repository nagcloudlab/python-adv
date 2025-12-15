# Level 15: Database Integration (SQLAlchemy)

## Learning Objectives
- Set up SQLAlchemy with FastAPI
- Create database models (ORM)
- Manage database sessions with dependencies
- Perform CRUD operations
- Define model relationships
- Query with filters and pagination

---

## Setup Instructions

```bash
cd level_15_database
pip install -r requirements.txt
uvicorn main:app --reload
```

**Note:** A SQLite database file (`tasks.db`) will be created automatically!

---

## Project Structure

```
level_15_database/
├── main.py                 # Entry point, creates tables
├── tasks.db               # SQLite database (auto-created)
└── app/
    ├── core/
    │   ├── config.py      # Settings (DATABASE_URL)
    │   └── database.py    # Engine, Session, get_db
    ├── models/
    │   └── models.py      # SQLAlchemy ORM models
    ├── schemas/
    │   ├── task.py        # Task Pydantic schemas
    │   └── user.py        # User Pydantic schemas
    └── routers/
        ├── tasks.py       # Task CRUD endpoints
        └── users.py       # User CRUD endpoints
```

---

## Key Concepts

### 1. Database Connection Setup
```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

### 2. Database Session Dependency
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoint
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### 3. SQLAlchemy Model
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    
    # Relationship
    tasks = relationship("Task", back_populates="owner")
```

### 4. Model with Foreign Key
```python
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship back to User
    owner = relationship("User", back_populates="tasks")
```

### 5. CRUD Operations

**Create:**
```python
db_user = User(username="john", email="john@example.com")
db.add(db_user)
db.commit()
db.refresh(db_user)  # Get generated id
```

**Read:**
```python
# Get all
users = db.query(User).all()

# Get by ID
user = db.query(User).filter(User.id == 1).first()

# Get with filter
active_users = db.query(User).filter(User.is_active == True).all()
```

**Update:**
```python
user = db.query(User).filter(User.id == 1).first()
user.username = "new_name"
db.commit()
db.refresh(user)
```

**Delete:**
```python
user = db.query(User).filter(User.id == 1).first()
db.delete(user)
db.commit()
```

### 6. Pydantic Schema with ORM Mode
```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    # Enable creating from SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)
```

---

## Database Relationships

### One-to-Many (User → Tasks)
```
User (1) ────< (Many) Task

user.tasks      # Get all user's tasks
task.owner      # Get task's owner
```

```python
# In User model
tasks = relationship("Task", back_populates="owner")

# In Task model
owner_id = Column(Integer, ForeignKey("users.id"))
owner = relationship("User", back_populates="tasks")
```

---

## SQLAlchemy Query Methods

| Method | Description |
|--------|-------------|
| `query(Model)` | Start a query |
| `filter(condition)` | WHERE clause |
| `filter_by(field=value)` | Simple WHERE |
| `first()` | Get first result |
| `all()` | Get all results |
| `one()` | Get exactly one (error if 0 or >1) |
| `count()` | Count results |
| `offset(n)` | Skip n records |
| `limit(n)` | Limit to n records |
| `order_by(field)` | Order results |
| `join(Model)` | JOIN tables |

---

## Testing the API

### 1. Create a User
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com"}'
```

### 2. Create a Task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn SQLAlchemy", "owner_id": 1, "priority": 5}'
```

### 3. List Tasks
```bash
curl "http://localhost:8000/tasks"
```

### 4. Get User with Tasks
```bash
curl "http://localhost:8000/users/1/with-tasks"
```

### 5. Filter Tasks
```bash
curl "http://localhost:8000/tasks?status=pending&priority=5"
```

---

## Exercises

### Exercise 1: Add Category Model
- Create a Category model
- Add many-to-many relationship with Task
- Create CRUD endpoints for categories

### Exercise 2: Add Pagination
- Create reusable pagination dependency
- Return total count, page, size with results

### Exercise 3: Soft Delete
- Add `is_deleted` field to models
- Modify queries to exclude deleted records
- Create "restore" endpoint

### Exercise 4: Search Endpoint
- Create `/search` endpoint
- Search across title and description
- Support sorting and pagination

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `no such table` | Tables not created | Check `Base.metadata.create_all()` |
| `UNIQUE constraint failed` | Duplicate unique value | Check if record exists first |
| `NOT NULL constraint` | Required field missing | Provide all required fields |
| `FOREIGN KEY constraint` | Invalid foreign key | Ensure referenced record exists |

---

## Database URL Examples

```python
# SQLite (file)
DATABASE_URL = "sqlite:///./app.db"

# SQLite (memory)
DATABASE_URL = "sqlite:///:memory:"

# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

---

## Best Practices

1. **Always use `get_db` dependency** - Ensures proper session cleanup
2. **Use Pydantic schemas** - Separate from SQLAlchemy models
3. **Handle not found** - Return 404 for missing records
4. **Use transactions** - Commit once per request
5. **Index frequently queried columns** - `index=True`
6. **Use relationship cascade** - For automatic cleanup

---

## What's Next?
**Level 16: Testing** - Learn to test FastAPI applications with pytest and TestClient.
