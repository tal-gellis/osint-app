from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import logging
import json
import os
import traceback
from uuid import uuid4
import pandas as pd
from storage import store_scan, get_all_scans, get_scan_by_id
from workers import run_osint_scan

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('exports', exist_ok=True)

app = FastAPI(
    title="OSINT Scanner API",
    description="API for running OSINT scans on domains using theHarvester and Amass",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DomainRequest(BaseModel):
    domain: str
    
    @validator('domain')
    def validate_domain(cls, v):
        # Basic domain validation to prevent command injection
        if not v or ' ' in v or ';' in v or '&' in v or '|' in v or '<' in v or '>' in v:
            raise ValueError('Invalid domain format')
        return v

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for logging errors"""
    error_id = str(uuid4())
    logger.error(json.dumps({
        "error_id": error_id,
        "path": request.url.path,
        "method": request.method,
        "error": str(exc),
        "traceback": traceback.format_exc()
    }))
    
    return JSONResponse(
        status_code=500,
        content={
            "error_id": error_id,
            "message": "An internal server error occurred. Please try again later."
        }
    )

@app.post("/scan")
async def scan_domain(request: DomainRequest, background_tasks: BackgroundTasks):
    """Start an OSINT scan for a domain"""
    try:
        scan_id = str(uuid4())
        start_time = datetime.utcnow()
        
        logger.info(json.dumps({
            "scan_id": scan_id,
            "domain": request.domain,
            "event": "scan_initiated"
        }))
        
        # Store initial scan with running status
        store_scan(scan_id, request.domain, start_time)
        
        # Run scan in background
        background_tasks.add_task(run_osint_scan, scan_id, request.domain, start_time)
        
        return {"scan_id": scan_id, "status": "started"}
    except Exception as e:
        logger.error(json.dumps({
            "domain": request.domain,
            "error": str(e),
            "event": "scan_initiation_failed"
        }))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scans")
def get_scans():
    """Get all scan records"""
    try:
        return get_all_scans()
    except Exception as e:
        logger.error(json.dumps({
            "error": str(e),
            "event": "get_scans_failed"
        }))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scans/{scan_id}")
def get_scan(scan_id: str):
    """Get a specific scan by ID"""
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@app.get("/export/{scan_id}")
def export_to_excel(scan_id: str):
    """Export scan results to Excel"""
    try:
        # Get scan data
        scan = get_scan_by_id(scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        if scan["results"] is None:
            raise HTTPException(status_code=400, detail="No results available for this scan")
        
        # Create Excel file
        export_path = f"exports/{scan_id}.xlsx"
        
        logger.info(json.dumps({
            "scan_id": scan_id,
            "event": "export_started"
        }))
        
        # Create a new Excel writer
        with pd.ExcelWriter(export_path, engine='xlsxwriter') as writer:
            # Create subdomains sheet
            if "subdomains" in scan["results"] and scan["results"]["subdomains"]:
                subdomains_df = pd.DataFrame(scan["results"]["subdomains"], columns=["Subdomain"])
                subdomains_df.to_excel(writer, sheet_name="Subdomains", index=False)
            
            # Create emails sheet
            if "emails" in scan["results"] and scan["results"]["emails"]:
                emails_df = pd.DataFrame(scan["results"]["emails"], columns=["Email"])
                emails_df.to_excel(writer, sheet_name="Emails", index=False)
            
            # Create IPs sheet
            if "ips" in scan["results"] and scan["results"]["ips"]:
                ips_df = pd.DataFrame(scan["results"]["ips"], columns=["IP Address"])
                ips_df.to_excel(writer, sheet_name="IP Addresses", index=False)
            
            # Create social profiles sheet
            if "social_profiles" in scan["results"] and scan["results"]["social_profiles"]:
                social_df = pd.DataFrame(scan["results"]["social_profiles"], columns=["Social Profile"])
                social_df.to_excel(writer, sheet_name="Social Profiles", index=False)
            
            # Create summary sheet
            summary_data = {
                "Domain": [scan["domain"]],
                "Status": [scan["status"]],
                "Start Time": [scan["start_time"]],
                "End Time": [scan["end_time"] or ""],
                "Subdomains Found": [len(scan["results"].get("subdomains", []))],
                "Emails Found": [len(scan["results"].get("emails", []))],
                "IPs Found": [len(scan["results"].get("ips", []))],
                "Social Profiles Found": [len(scan["results"].get("social_profiles", []))]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        logger.info(json.dumps({
            "scan_id": scan_id,
            "event": "export_completed",
            "file_path": export_path
        }))
        
        return FileResponse(
            path=export_path,
            filename=f"osint_scan_{scan['domain']}_{scan_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(json.dumps({
            "scan_id": scan_id,
            "error": str(e),
            "event": "export_failed"
        }))
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/")
def read_root():
    """API health check endpoint"""
    return {
        "status": "online",
        "api_version": "1.0.0",
        "endpoints": [
            {"path": "/scan", "method": "POST", "description": "Start a new domain scan"},
            {"path": "/scans", "method": "GET", "description": "Get all scans"},
            {"path": "/scans/{scan_id}", "method": "GET", "description": "Get a specific scan"},
            {"path": "/export/{scan_id}", "method": "GET", "description": "Export scan results to Excel"}
        ]
    }
