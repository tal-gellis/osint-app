# storage.py
import sqlite3
import json
import os
from datetime import datetime

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# SQLite database file
DB_FILE = 'data/osint_scans.db'

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create scans table if it doesn't exist
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

# Initialize the database
init_db()

def store_scan(scan_id, domain, start_time):
    """Store initial scan record in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO scans (scan_id, domain, start_time, status) VALUES (?, ?, ?, ?)',
        (scan_id, domain, start_time.isoformat(), 'running')
    )
    
    conn.commit()
    conn.close()

def update_scan_results(scan_id, results, end_time):
    """Update scan with results and completion time."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Convert results to JSON string for storage
    results_json = json.dumps(results)
    
    cursor.execute(
        'UPDATE scans SET results = ?, end_time = ?, status = ? WHERE scan_id = ?',
        (results_json, end_time.isoformat(), 'completed', scan_id)
    )
    
    conn.commit()
    conn.close()

def get_all_scans():
    """Get all stored scans from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT scan_id, domain, start_time, end_time, results, status FROM scans')
    rows = cursor.fetchall()
    
    scans = []
    for row in rows:
        scan_id, domain, start_time, end_time, results_json, status = row
        
        scan = {
            'scan_id': scan_id,
            'domain': domain,
            'start_time': start_time,
            'end_time': end_time,
            'status': status,
            'results': json.loads(results_json) if results_json else None
        }
        scans.append(scan)
    
    conn.close()
    return scans

def get_scan_by_id(scan_id):
    """Get a specific scan by ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT scan_id, domain, start_time, end_time, results, status FROM scans WHERE scan_id = ?',
        (scan_id,)
    )
    row = cursor.fetchone()
    
    if row:
        scan_id, domain, start_time, end_time, results_json, status = row
        
        scan = {
            'scan_id': scan_id,
            'domain': domain,
            'start_time': start_time,
            'end_time': end_time,
            'status': status,
            'results': json.loads(results_json) if results_json else None
        }
        conn.close()
        return scan
    
    conn.close()
    return None
