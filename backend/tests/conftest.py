import pytest
import sys
import os
import tempfile
import sqlite3
import shutil

# Add the parent directory to sys.path so tests can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def temp_db():
    """Fixture that provides a temporary SQLite database for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create a test database file
    db_path = os.path.join(temp_dir, 'test_osint_scans.db')
    
    # Set this as the database path for the module
    import storage
    storage.DB_FILE = db_path
    
    # Initialize the database with required schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        scan_id TEXT PRIMARY KEY,
        domain TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        results TEXT,
        status TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    
    # Return the path to the test database
    yield db_path
    
    # Cleanup after the test
    shutil.rmtree(temp_dir) 