from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging
import json
import os
import traceback
from uuid import uuid4
import pandas as pd
from storage import store_scan, get_all_scans, get_scan_by_id
from workers import start_scan

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

# Create FastAPI application
app = FastAPI(
    title="OSINT Scanner API",
    description="API for running OSINT scans on domains using theHarvester and Amass",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class ScanRequest(BaseModel):
    domain: str
    options: Optional[Dict[str, bool]] = None

# Define error response model
class ErrorResponse(BaseModel):
    detail: str

# Define routes
@app.post("/api/scan", response_model=Dict[str, str])
async def api_start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start a new scan for the given domain using selected OSINT tools
    """
    try:
        logger.info(f"Starting scan for domain: {request.domain}")
        
        # Validate domain format
        if not request.domain or '.' not in request.domain:
            raise HTTPException(status_code=400, detail="Invalid domain format")
        
        # Start the scan in the background
        result = await start_scan(request.domain, request.options)
        
        return result
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to start scan: {str(e)}")

@app.get("/api/scan/{scan_id}", response_model=Dict[str, Any])
async def get_scan_status(scan_id: str):
    """
    Get the status and results of a specific scan
    """
    try:
        scan = get_scan_by_id(scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail=f"Scan with ID {scan_id} not found")
        
        return scan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scan {scan_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scan: {str(e)}")

@app.get("/api/scans", response_model=List[Dict[str, Any]])
async def get_scans():
    """
    Get all scans
    """
    try:
        scans = get_all_scans()
        return scans
    except Exception as e:
        logger.error(f"Error retrieving scans: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scans: {str(e)}")

@app.get("/api/scan/{scan_id}/export")
async def export_scan(scan_id: str):
    """
    Export scan results to Excel
    """
    try:
        scan = get_scan_by_id(scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail=f"Scan with ID {scan_id} not found")
        
        # Create Excel file
        filename = f"exports/osint-scan-{scan_id}.xlsx"
        
        # Create a Pandas Excel writer
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        
        # Write each category to a separate sheet
        if "details" in scan:
            # Subdomains sheet
            if "subdomains" in scan["details"]:
                subdomains_df = pd.DataFrame(scan["details"]["subdomains"], columns=["Subdomain"])
                subdomains_df.to_excel(writer, sheet_name="Subdomains", index=False)
            
            # Emails sheet
            if "emails" in scan["details"]:
                emails_df = pd.DataFrame(scan["details"]["emails"], columns=["Email"])
                emails_df.to_excel(writer, sheet_name="Emails", index=False)
            
            # IPs sheet
            if "ips" in scan["details"]:
                ips_df = pd.DataFrame(scan["details"]["ips"], columns=["IP Address"])
                ips_df.to_excel(writer, sheet_name="IP Addresses", index=False)
            
            # Social profiles sheet
            if "social_profiles" in scan["details"]:
                social_df = pd.DataFrame(scan["details"]["social_profiles"], columns=["Social Profile"])
                social_df.to_excel(writer, sheet_name="Social Profiles", index=False)
        
        # Save the Excel file
        writer.close()
        
        # Return the file as a download
        return FileResponse(
            path=filename, 
            filename=f"osint-scan-{scan_id}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting scan {scan_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to export scan: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    ) 