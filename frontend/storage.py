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

def update_scan_results(scan_id, scan_result):
    """Update scan with complete scan result object.
    
    Args:
        scan_id (str): The ID of the scan to update
        scan_result (dict): Complete scan result object with all fields
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Convert results to JSON string for storage
    results_json = json.dumps(scan_result)

    cursor.execute(
        'UPDATE scans SET domain = ?, start_time = ?, end_time = ?, results = ?, status = ? WHERE scan_id = ?',
        (
            scan_result.get('domain', ''),
            scan_result.get('startTime', ''),
            scan_result.get('endTime', ''),
            results_json,
            'completed',
            scan_id
        )
    )

    # If no rows were updated, this is a new scan, so insert it
    if cursor.rowcount == 0:
        cursor.execute(
            'INSERT INTO scans (scan_id, domain, start_time, end_time, results, status) VALUES (?, ?, ?, ?, ?, ?)',
            (
                scan_id,
                scan_result.get('domain', ''),
                scan_result.get('startTime', ''),
                scan_result.get('endTime', ''),
                results_json,
                'completed'
            )
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
        
        try:
            # Try to parse the JSON results
            results = json.loads(results_json) if results_json else None
            
            # If we have parsed results, use them directly
            if results and isinstance(results, dict):
                # Add scan_id if missing
                if 'id' not in results:
                    results['id'] = scan_id
                scans.append(results)
            else:
                # Otherwise construct a scan object from the database fields
                scan = {
                    'id': scan_id,
                    'domain': domain,
                    'startTime': start_time,
                    'endTime': end_time,
                    'status': status,
                    'summary': {'subdomains': 0, 'emails': 0, 'ips': 0, 'socialProfiles': 0},
                    'details': {'subdomains': [], 'emails': [], 'ips': [], 'social_profiles': []}
                }
                scans.append(scan)
        except (json.JSONDecodeError, TypeError):
            # Handle malformed JSON
            scan = {
                'id': scan_id,
                'domain': domain,
                'startTime': start_time,
                'endTime': end_time,
                'status': status,
                'summary': {'subdomains': 0, 'emails': 0, 'ips': 0, 'socialProfiles': 0},
                'details': {'subdomains': [], 'emails': [], 'ips': [], 'social_profiles': []}
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
        
        try:
            # Try to parse the JSON results
            results = json.loads(results_json) if results_json else None
            
            # If we have parsed results, use them directly
            if results and isinstance(results, dict):
                # Add scan_id if missing
                if 'id' not in results:
                    results['id'] = scan_id
                conn.close()
                return results
            else:
                # Otherwise construct a scan object from the database fields
                scan = {
                    'id': scan_id,
                    'domain': domain,
                    'startTime': start_time,
                    'endTime': end_time,
                    'status': status,
                    'summary': {'subdomains': 0, 'emails': 0, 'ips': 0, 'socialProfiles': 0},
                    'details': {'subdomains': [], 'emails': [], 'ips': [], 'social_profiles': []}
                }
                conn.close()
                return scan
        except (json.JSONDecodeError, TypeError):
            # Handle malformed JSON
            scan = {
                'id': scan_id,
                'domain': domain,
                'startTime': start_time,
                'endTime': end_time,
                'status': status,
                'summary': {'subdomains': 0, 'emails': 0, 'ips': 0, 'socialProfiles': 0},
                'details': {'subdomains': [], 'emails': [], 'ips': [], 'social_profiles': []}
            }
            conn.close()
            return scan

    conn.close()
    return None 