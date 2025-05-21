import pytest
import sqlite3
import json
from datetime import datetime
import os

# Import the storage functions to test
from storage import (
    store_scan,
    update_scan_results,
    get_scan_by_id,
    get_all_scans,
    DB_FILE
)

def test_store_scan(temp_db):
    """Test storing a scan in the database"""
    scan_id = "test-scan-1"
    domain = "example.com"
    start_time = datetime.now()
    
    # Store a scan
    store_scan(scan_id, domain, start_time)
    
    # Retrieve the scan to verify it was stored
    scan = get_scan_by_id(scan_id)
    
    # Check scan was stored correctly
    assert scan is not None
    assert scan["scan_id"] == scan_id
    assert scan["domain"] == domain
    assert scan["status"] == "running"  # Default status when creating a scan

def test_update_scan_results(temp_db):
    """Test updating scan results in the database"""
    scan_id = "test-scan-2"
    domain = "example.com"
    start_time = datetime.now()
    
    # First, store a scan
    store_scan(scan_id, domain, start_time)
    
    # Create sample results
    results = {
        "subdomains": ["sub1.example.com", "sub2.example.com"],
        "emails": ["admin@example.com"],
        "ips": ["1.1.1.1"],
        "social_profiles": []
    }
    end_time = datetime.now()
    
    # Update scan with results
    update_scan_results(scan_id, results, end_time)
    
    # Retrieve the scan to verify the update
    scan = get_scan_by_id(scan_id)
    
    # Check scan was updated correctly
    assert scan["status"] == "completed"
    assert scan["results"] is not None
    assert "subdomains" in scan["results"]
    assert "emails" in scan["results"]

def test_get_scan_by_id(temp_db):
    """Test retrieving a scan by ID"""
    scan_id = "test-scan-3"
    domain = "example.com"
    start_time = datetime.now()
    
    # Store a scan with results
    store_scan(scan_id, domain, start_time)
    
    results = {
        "subdomains": ["sub1.example.com"],
        "emails": ["admin@example.com"],
        "ips": ["1.1.1.1"],
        "social_profiles": []
    }
    update_scan_results(scan_id, results, datetime.now())
    
    # Retrieve it using get_scan_by_id
    scan = get_scan_by_id(scan_id)
    
    # Verify retrieval works correctly
    assert scan is not None
    assert scan["scan_id"] == scan_id
    assert scan["domain"] == domain
    assert scan["status"] == "completed"
    assert "results" in scan
    assert "subdomains" in scan["results"]
    assert scan["results"]["subdomains"][0] == "sub1.example.com"

def test_get_all_scans(temp_db):
    """Test retrieving all scans"""
    # Clear the database
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM scans")
    conn.commit()
    conn.close()
    
    # Store multiple scans
    scan_ids = ["test-scan-4", "test-scan-5", "test-scan-6"]
    domains = ["example.com", "test.com", "sample.org"]
    
    for i in range(3):
        store_scan(scan_ids[i], domains[i], datetime.now())
    
    # Retrieve all scans
    scans = get_all_scans()
    
    # Verify we get all 3 scans
    assert len(scans) == 3
    
    # Verify scan data is correct
    for scan in scans:
        assert scan["scan_id"] in scan_ids
        index = scan_ids.index(scan["scan_id"])
        assert scan["domain"] == domains[index]
        assert scan["status"] == "running" 