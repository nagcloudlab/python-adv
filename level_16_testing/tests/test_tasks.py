"""
Test Task Endpoints
===================
Comprehensive tests for task CRUD operations.

Run: pytest tests/test_tasks.py -v
"""

import pytest


class TestListTasks:
    """Tests for GET /tasks"""
    
    def test_list_tasks_returns_list(self, client):
        """Test that list tasks returns a list"""
        response = client.get("/tasks")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_tasks_has_seed_data(self, client):
        """Test that database has seed tasks"""
        response = client.get("/tasks")
        tasks = response.json()
        
        # Database is seeded with 2 tasks
        assert len(tasks) >= 2
    
    def test_list_tasks_filter_by_status(self, client):
        """Test filtering tasks by status"""
        response = client.get("/tasks?status=pending")
        tasks = response.json()
        
        # All returned tasks should be pending
        for task in tasks:
            assert task["status"] == "pending"
    
    def test_list_tasks_filter_by_priority(self, client):
        """Test filtering tasks by priority"""
        response = client.get("/tasks?priority=5")
        tasks = response.json()
        
        for task in tasks:
            assert task["priority"] == 5


class TestGetTask:
    """Tests for GET /tasks/{id}"""
    
    def test_get_task_success(self, client):
        """Test getting a task that exists"""
        response = client.get("/tasks/1")
        
        assert response.status_code == 200
        assert response.json()["id"] == 1
    
    def test_get_task_not_found(self, client):
        """Test getting a task that doesn't exist"""
        response = client.get("/tasks/9999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_task_has_required_fields(self, client):
        """Test that task response has all required fields"""
        response = client.get("/tasks/1")
        task = response.json()
        
        required_fields = ["id", "title", "status", "priority", "created_at"]
        for field in required_fields:
            assert field in task


class TestCreateTask:
    """Tests for POST /tasks"""
    
    def test_create_task_success(self, auth_client, sample_task):
        """Test creating a task with valid data"""
        response = auth_client.post("/tasks", json=sample_task)
        
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == sample_task["title"]
        assert data["priority"] == sample_task["priority"]
        assert "id" in data
    
    def test_create_task_without_auth(self, client, sample_task):
        """Test that creating task requires authentication"""
        response = client.post("/tasks", json=sample_task)
        
        assert response.status_code == 401
    
    def test_create_task_minimal_data(self, auth_client):
        """Test creating task with only required field"""
        response = auth_client.post("/tasks", json={"title": "Minimal Task"})
        
        assert response.status_code == 201
        assert response.json()["title"] == "Minimal Task"
        assert response.json()["priority"] == 1  # Default
    
    def test_create_task_invalid_title_too_short(self, auth_client):
        """Test validation: title too short"""
        response = auth_client.post("/tasks", json={"title": "AB"})
        
        assert response.status_code == 422  # Validation error
    
    def test_create_task_invalid_priority(self, auth_client):
        """Test validation: priority out of range"""
        response = auth_client.post(
            "/tasks",
            json={"title": "Test Task", "priority": 10}
        )
        
        assert response.status_code == 422
    
    def test_create_task_returns_id(self, auth_client, sample_task):
        """Test that created task has an ID"""
        response = auth_client.post("/tasks", json=sample_task)
        
        assert "id" in response.json()
        assert isinstance(response.json()["id"], int)


class TestUpdateTask:
    """Tests for PUT /tasks/{id}"""
    
    def test_update_task_success(self, auth_client, created_task):
        """Test updating a task"""
        task_id = created_task["id"]
        
        response = auth_client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated Title"}
        )
        
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
    
    def test_update_task_status(self, auth_client, created_task):
        """Test updating task status"""
        task_id = created_task["id"]
        
        response = auth_client.put(
            f"/tasks/{task_id}",
            json={"status": "completed"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
    
    def test_update_task_not_found(self, auth_client):
        """Test updating non-existent task"""
        response = auth_client.put(
            "/tasks/9999",
            json={"title": "New Title"}
        )
        
        assert response.status_code == 404
    
    def test_update_task_without_auth(self, client):
        """Test that update requires authentication"""
        response = client.put("/tasks/1", json={"title": "New"})
        
        assert response.status_code == 401


class TestDeleteTask:
    """Tests for DELETE /tasks/{id}"""
    
    def test_delete_task_success(self, auth_client, created_task):
        """Test deleting a task"""
        task_id = created_task["id"]
        
        response = auth_client.delete(f"/tasks/{task_id}")
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = auth_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404
    
    def test_delete_task_not_found(self, auth_client):
        """Test deleting non-existent task"""
        response = auth_client.delete("/tasks/9999")
        
        assert response.status_code == 404
    
    def test_delete_task_without_auth(self, client):
        """Test that delete requires authentication"""
        response = client.delete("/tasks/1")
        
        assert response.status_code == 401


class TestTaskStats:
    """Tests for GET /tasks/stats/summary"""
    
    def test_stats_returns_total(self, client):
        """Test that stats includes total count"""
        response = client.get("/tasks/stats/summary")
        
        assert response.status_code == 200
        assert "total" in response.json()
    
    def test_stats_by_status(self, client):
        """Test that stats includes status breakdown"""
        response = client.get("/tasks/stats/summary")
        data = response.json()
        
        assert "by_status" in data
        assert isinstance(data["by_status"], dict)


# ============================================================
# Parameterized Tests
# ============================================================

@pytest.mark.parametrize("priority", [1, 2, 3, 4, 5])
def test_create_task_valid_priorities(auth_client, priority):
    """Test creating tasks with all valid priority values"""
    response = auth_client.post(
        "/tasks",
        json={"title": f"Priority {priority} Task", "priority": priority}
    )
    
    assert response.status_code == 201
    assert response.json()["priority"] == priority


@pytest.mark.parametrize("invalid_priority", [0, -1, 6, 100])
def test_create_task_invalid_priorities(auth_client, invalid_priority):
    """Test that invalid priorities are rejected"""
    response = auth_client.post(
        "/tasks",
        json={"title": "Test", "priority": invalid_priority}
    )
    
    assert response.status_code == 422


@pytest.mark.parametrize("status", ["pending", "in_progress", "completed"])
def test_update_task_valid_statuses(auth_client, created_task, status):
    """Test updating task with all valid status values"""
    response = auth_client.put(
        f"/tasks/{created_task['id']}",
        json={"status": status}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == status
