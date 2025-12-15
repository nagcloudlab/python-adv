# Level 16: Testing FastAPI Applications

## Learning Objectives
- Write tests with pytest
- Use TestClient for API testing
- Create test fixtures
- Test CRUD endpoints
- Test authentication
- Mock dependencies
- Organize tests properly

---

## Setup Instructions

```bash
cd level_16_testing
pip install -r requirements.txt

# Run tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_tasks.py -v

# Run tests matching pattern
pytest -k "create" -v
```

---

## Project Structure

```
level_16_testing/
├── main.py                 # FastAPI app
├── app/
│   ├── database.py         # In-memory database
│   ├── schemas.py          # Pydantic models
│   ├── dependencies.py     # Auth dependencies
│   └── routers/
│       └── tasks.py        # Task endpoints
├── tests/
│   ├── conftest.py         # Shared fixtures
│   ├── test_main.py        # Root endpoint tests
│   ├── test_tasks.py       # Task CRUD tests
│   └── test_auth.py        # Authentication tests
└── requirements.txt
```

---

## Key Concepts

### 1. TestClient Basics
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello"
```

### 2. Test Fixtures (conftest.py)
```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """TestClient fixture"""
    return TestClient(app)

@pytest.fixture
def auth_client(client):
    """Authenticated client"""
    client.headers["X-API-Key"] = "valid-key"
    return client
```

### 3. Testing CRUD Operations
```python
# CREATE
def test_create(auth_client):
    response = auth_client.post("/items", json={"name": "Test"})
    assert response.status_code == 201

# READ
def test_read(client):
    response = client.get("/items/1")
    assert response.status_code == 200

# UPDATE
def test_update(auth_client):
    response = auth_client.put("/items/1", json={"name": "Updated"})
    assert response.status_code == 200

# DELETE
def test_delete(auth_client):
    response = auth_client.delete("/items/1")
    assert response.status_code == 204
```

### 4. Testing Authentication
```python
def test_no_auth_returns_401(client):
    response = client.post("/protected", json={})
    assert response.status_code == 401

def test_valid_auth_succeeds(auth_client):
    response = auth_client.post("/protected", json={})
    assert response.status_code == 200
```

### 5. Parameterized Tests
```python
@pytest.mark.parametrize("status_code,path", [
    (200, "/"),
    (200, "/health"),
    (404, "/nonexistent"),
])
def test_endpoints(client, status_code, path):
    response = client.get(path)
    assert response.status_code == status_code
```

### 6. Dependency Override
```python
def test_with_mock_user(client):
    from main import app
    from app.dependencies import get_current_user
    
    def mock_user():
        return {"id": 1, "role": "admin"}
    
    app.dependency_overrides[get_current_user] = mock_user
    
    try:
        response = client.get("/me")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

---

## Running Tests

### Basic Commands
```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run specific file
pytest tests/test_tasks.py

# Run specific test
pytest tests/test_tasks.py::TestCreateTask::test_create_task_success

# Run tests matching pattern
pytest -k "create"
pytest -k "test_create or test_update"
```

### Test Coverage
```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

---

## Fixture Scopes

| Scope | Description |
|-------|-------------|
| `function` (default) | Run once per test |
| `class` | Run once per test class |
| `module` | Run once per module |
| `session` | Run once per test session |

```python
@pytest.fixture(scope="session")
def expensive_setup():
    """Only runs once for all tests"""
    return setup_database()
```

---

## Common Assertions

```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201  # Created
assert response.status_code == 204  # No Content
assert response.status_code == 400  # Bad Request
assert response.status_code == 401  # Unauthorized
assert response.status_code == 404  # Not Found
assert response.status_code == 422  # Validation Error

# Response body
assert response.json()["key"] == "value"
assert "field" in response.json()
assert isinstance(response.json(), list)
assert len(response.json()) == 5

# Headers
assert response.headers["content-type"] == "application/json"
```

---

## Testing Patterns

### Pattern 1: Arrange-Act-Assert
```python
def test_create_task(auth_client):
    # Arrange
    task_data = {"title": "Test", "priority": 3}
    
    # Act
    response = auth_client.post("/tasks", json=task_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["title"] == "Test"
```

### Pattern 2: Given-When-Then
```python
def test_update_task():
    # Given: A task exists
    # When: I update the task
    # Then: The task is updated
    pass
```

### Pattern 3: Test Classes
```python
class TestTaskCRUD:
    """Group related tests"""
    
    def test_create(self, auth_client):
        ...
    
    def test_read(self, client):
        ...
    
    def test_update(self, auth_client):
        ...
    
    def test_delete(self, auth_client):
        ...
```

---

## Exercises

### Exercise 1: Add More Tests
Add tests for:
- Updating task with invalid status
- Creating task with very long title
- Filtering tasks by multiple criteria

### Exercise 2: Test Database Reset
Write tests that verify:
- Database resets between tests
- Created data doesn't leak

### Exercise 3: Test Edge Cases
Add tests for:
- Empty request body
- Special characters in title
- Concurrent requests

### Exercise 4: Coverage Report
- Install pytest-cov
- Generate coverage report
- Achieve 90%+ coverage

---

## Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** - `test_create_task_with_invalid_priority_returns_422`
3. **Use fixtures** - Don't repeat setup code
4. **Test edge cases** - Empty, null, boundary values
5. **Independent tests** - Tests shouldn't depend on each other
6. **Clean up** - Reset state after tests

---

## What's Next?
**Level 17: WebSockets** - Learn real-time communication with WebSockets in FastAPI.
