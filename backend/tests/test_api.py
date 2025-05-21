import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns 200 OK"""
    response = client.get("/")
    assert response.status_code == 200
    
def test_scan_valid_domain():
    """Test scanning a valid domain"""
    response = client.post(
        "/scan",
        json={"domain": "example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert "status" in data
    
def test_scan_invalid_domain():
    """Test that invalid domain input is rejected"""
    response = client.post(
        "/scan",
        json={"domain": "invalid domain with spaces"}
    )
    assert response.status_code == 422  # Validation error

def test_get_all_scans():
    """Test retrieving all scans"""
    response = client.get("/scans")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 