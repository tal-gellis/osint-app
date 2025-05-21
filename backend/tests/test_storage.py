import pytest
import os
import sqlite3
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
import tempfile

# Import the storage functions to test
from storage import (
    store_scan,
    update_scan_results,
    get_scan_by_id,
    get_all_scans
)

# Create a temporary database for testing
@pytest.fixture
def temp_db():
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    # Patch the database path to use our temporary file
    with patch('storage.DB_PATH', temp_file.name):
        # Initialize the database schema in the temporary file
        conn = sqlite3.connect(temp_file.name)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            domain TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            status TEXT NOT NULL,
            results TEXT
        )
        ''')
        conn.commit()
        conn.close()
        
        yield temp_file.name
    
    # Cleanup - delete the temporary file
    os.unlink(temp_file.name)

def test_store_scan(temp_db):
    """Test storing a new scan in the database"""
    # Patch the DB_PATH to use our temporary DB
    with patch('storage.DB_PATH', temp_db):
        scan_id = "test-scan-1"
        domain = "example.com"
        start_time = datetime.now()
        
        # Store a scan
        store_scan(scan_id, domain, start_time)
        
        # Retrieve it from the database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id, domain, status FROM scans WHERE id = ?", (scan_id,))
        result = cursor.fetchone()
        conn.close()
        
        # Verify scan was stored correctly
        assert result is not None
        assert result[0] == scan_id
        assert result[1] == domain
        assert result[2] == "running"  # Default status when creating a scan

def test_update_scan_results(temp_db):
    """Test updating scan results"""
    # Patch the DB_PATH to use our temporary DB
    with patch('storage.DB_PATH', temp_db):
        scan_id = "test-scan-2"
        domain = "example.com"
        start_time = datetime.now()
        
        # First, store a scan
        store_scan(scan_id, domain, start_time)
        
        # Now update it with results
        results = {
            "subdomains": ["sub1.example.com", "sub2.example.com"],
            "emails": ["admin@example.com"],
            "ips": ["1.1.1.1"],
            "social_profiles": []
        }
        end_time = datetime.now()
        
        update_scan_results(scan_id, results, end_time)
        
        # Retrieve it from the database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT status, results, end_time FROM scans WHERE id = ?", (scan_id,))
        result = cursor.fetchone()
        conn.close()
        
        # Verify scan was updated correctly
        assert result is not None
        assert result[0] == "completed"  # Status should be updated
        
        # Check results were stored as JSON
        stored_results = json.loads(result[1])
        assert "subdomains" in stored_results
        assert len(stored_results["subdomains"]) == 2
        assert "emails" in stored_results
        assert stored_results["emails"][0] == "admin@example.com"
        
        # Check end_time was updated
        assert result[2] is not None

def test_get_scan_by_id(temp_db):
    """Test retrieving a scan by ID"""
    # Patch the DB_PATH to use our temporary DB
    with patch('storage.DB_PATH', temp_db):
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
    # Patch the DB_PATH to use our temporary DB
    with patch('storage.DB_PATH', temp_db):
        # Clear the database
        conn = sqlite3.connect(temp_db)
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