import pytest
from fastapi.testclient import TestClient
from main import app
import json
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_read_root():
    """Test the root endpoint returns correct data"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "online"
    assert "endpoints" in data
    
def test_scan_domain_success():
    """Test the scan endpoint with valid domain"""
    # Mock the background task execution to avoid actual tool execution
    with patch('main.run_osint_scan') as mock_run_scan:
        response = client.post(
            "/scan",
            json={"domain": "example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        assert "status" in data
        assert data["status"] == "started"
        
        # Verify the background task was called
        mock_run_scan.assert_called_once()

def test_scan_domain_invalid():
    """Test the scan endpoint with invalid domain"""
    response = client.post(
        "/scan",
        json={"domain": "invalid domain with spaces"}
    )
    assert response.status_code == 422  # Validation error

def test_get_scans():
    """Test getting all scans"""
    # Mock the storage function to return a predefined response
    with patch('main.get_all_scans') as mock_get_scans:
        mock_get_scans.return_value = [
            {
                "scan_id": "test-id-1",
                "domain": "example.com",
                "start_time": "2025-05-20T00:00:00",
                "status": "completed"
            }
        ]
        response = client.get("/scans")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["domain"] == "example.com"

def test_get_scan_by_id_success():
    """Test getting a scan by ID when it exists"""
    # Mock the storage function to return a predefined response
    with patch('main.get_scan_by_id') as mock_get_scan:
        mock_get_scan.return_value = {
            "scan_id": "test-id-1",
            "domain": "example.com",
            "start_time": "2025-05-20T00:00:00",
            "status": "completed",
            "results": {
                "subdomains": ["sub1.example.com", "sub2.example.com"],
                "emails": ["admin@example.com"],
                "ips": ["1.1.1.1"],
                "social_profiles": []
            }
        }
        response = client.get("/scans/test-id-1")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "example.com"
        assert "results" in data
        assert len(data["results"]["subdomains"]) == 2

def test_get_scan_by_id_not_found():
    """Test getting a scan by ID when it does not exist"""
    # Mock the storage function to return None
    with patch('main.get_scan_by_id') as mock_get_scan:
        mock_get_scan.return_value = None
        response = client.get("/scans/nonexistent-id")
        assert response.status_code == 404 