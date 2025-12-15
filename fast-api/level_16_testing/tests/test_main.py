"""
Test Main/Root Endpoints
========================
Basic tests for root endpoints.

Run: pytest tests/test_main.py -v
"""

import pytest


class TestRootEndpoints:
    """Tests for root endpoints"""
    
    def test_root_returns_200(self, client):
        """
        Test that root endpoint returns 200 OK
        
        This is the simplest possible test:
        1. Make a GET request to /
        2. Check status code is 200
        """
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_returns_message(self, client):
        """
        Test that root endpoint returns expected message
        """
        response = client.get("/")
        data = response.json()
        
        assert "message" in data
        assert "Level 16" in data["message"]
    
    def test_health_check(self, client):
        """
        Test health check endpoint
        """
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_info_endpoint(self, client):
        """
        Test info endpoint returns concepts
        """
        response = client.get("/info")
        data = response.json()
        
        assert response.status_code == 200
        assert "concepts" in data
        assert isinstance(data["concepts"], list)


# ============================================================
# Function-based tests (alternative style)
# ============================================================

def test_root_status_code(client):
    """Simple function-based test"""
    response = client.get("/")
    assert response.status_code == 200


def test_root_content_type(client):
    """Test response content type"""
    response = client.get("/")
    assert response.headers["content-type"] == "application/json"


def test_nonexistent_endpoint(client):
    """Test 404 for nonexistent endpoint"""
    response = client.get("/nonexistent")
    assert response.status_code == 404
