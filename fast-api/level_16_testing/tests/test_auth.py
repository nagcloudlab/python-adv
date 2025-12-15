"""
Test Authentication
===================
Tests for authentication and authorization.

Run: pytest tests/test_auth.py -v
"""

import pytest


class TestAuthentication:
    """Tests for API key authentication"""
    
    def test_no_api_key_returns_401(self, client):
        """Test that protected endpoints require API key"""
        response = client.post("/tasks", json={"title": "Test"})
        
        assert response.status_code == 401
        assert "API key" in response.json()["detail"]
    
    def test_invalid_api_key_returns_401(self, client):
        """Test that invalid API key is rejected"""
        client.headers["X-API-Key"] = "invalid-key"
        response = client.post("/tasks", json={"title": "Test"})
        
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]
    
    def test_valid_api_key_succeeds(self, auth_client):
        """Test that valid API key is accepted"""
        response = auth_client.post("/tasks", json={"title": "Test Task"})
        
        assert response.status_code == 201
    
    def test_public_endpoints_no_auth(self, client):
        """Test that public endpoints don't require auth"""
        # These should work without authentication
        assert client.get("/").status_code == 200
        assert client.get("/tasks").status_code == 200
        assert client.get("/tasks/1").status_code == 200


class TestDifferentUsers:
    """Tests with different user types"""
    
    def test_admin_can_create_task(self, auth_client):
        """Test admin can create tasks"""
        response = auth_client.post("/tasks", json={"title": "Admin Task"})
        assert response.status_code == 201
    
    def test_user_can_create_task(self, user_client):
        """Test regular user can create tasks"""
        response = user_client.post("/tasks", json={"title": "User Task"})
        assert response.status_code == 201


# ============================================================
# Testing with Mocked Dependencies
# ============================================================

class TestMockedAuth:
    """
    Example of testing with mocked dependencies
    
    This demonstrates how to override dependencies for testing
    """
    
    def test_with_dependency_override(self, client):
        """
        Test using dependency override
        
        We can replace real dependencies with test versions
        """
        from main import app
        from app.dependencies import get_current_user
        
        # Create a mock user
        def mock_get_current_user():
            return {"username": "test_user", "role": "admin"}
        
        # Override the dependency
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            # Now requests will use our mock user
            response = client.post("/tasks", json={"title": "Test"})
            assert response.status_code == 201
        finally:
            # Clean up - remove override
            app.dependency_overrides.clear()
    
    def test_override_returns_specific_user(self, client):
        """Test with specific user data"""
        from main import app
        from app.dependencies import get_current_user
        
        # Mock with specific data
        def mock_user():
            return {
                "username": "mock_user",
                "role": "user",
                "api_key": "mock-key"
            }
        
        app.dependency_overrides[get_current_user] = mock_user
        
        try:
            response = client.post(
                "/tasks",
                json={"title": "Test Task"}
            )
            assert response.status_code == 201
        finally:
            app.dependency_overrides.clear()


# ============================================================
# Edge Cases
# ============================================================

class TestAuthEdgeCases:
    """Edge cases for authentication"""
    
    def test_empty_api_key(self, client):
        """Test with empty API key"""
        client.headers["X-API-Key"] = ""
        response = client.post("/tasks", json={"title": "Test"})
        
        # Empty string should be treated as no key
        assert response.status_code == 401
    
    def test_whitespace_api_key(self, client):
        """Test with whitespace API key"""
        client.headers["X-API-Key"] = "   "
        response = client.post("/tasks", json={"title": "Test"})
        
        assert response.status_code == 401
    
    def test_case_sensitive_api_key(self, client):
        """Test that API keys are case-sensitive"""
        client.headers["X-API-Key"] = "ADMIN-KEY-123"  # Wrong case
        response = client.post("/tasks", json={"title": "Test"})
        
        assert response.status_code == 401
