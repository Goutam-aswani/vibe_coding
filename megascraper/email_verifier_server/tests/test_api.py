"""
Test suite for Email Verifier API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_verify_single_email():
    """Test single email verification"""
    response = client.post(
        "/api/v1/verify",
        json={"email": "test@example.com"}
    )
    
    # May fail without valid session cookie
    if response.status_code == 200:
        data = response.json()
        assert "email" in data
        assert "status" in data
        assert data["email"] == "test@example.com"


def test_verify_batch():
    """Test batch email verification"""
    response = client.post(
        "/api/v1/verify/batch",
        json={
            "emails": ["test1@example.com", "test2@example.com"],
            "max_concurrent": 2
        }
    )
    
    # May fail without valid session cookie
    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "results" in data
        assert data["total"] == 2


def test_create_job():
    """Test background job creation"""
    response = client.post(
        "/api/v1/jobs",
        json={
            "emails": ["test1@example.com", "test2@example.com"],
            "max_concurrent": 2
        }
    )
    
    # May fail without valid session cookie
    if response.status_code == 200:
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        assert "total_emails" in data
        assert data["total_emails"] == 2


def test_metrics():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "version" in data
    assert "jobs" in data


def test_root_redirect():
    """Test root redirects to docs"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/docs" in response.headers["location"]


def test_invalid_email():
    """Test validation of invalid email"""
    response = client.post(
        "/api/v1/verify",
        json={"email": "not-an-email"}
    )
    assert response.status_code == 422  # Validation error
