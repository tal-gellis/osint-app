from datetime import datetime
import subprocess
import socket
import dns.resolver
import requests
from bs4 import BeautifulSoup
from storage import update_scan_results
import time
import asyncio
import json
import uuid
import os
import re
from typing import Dict, List, Any, Optional
import logging
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class OsintToolResult:
    """Base class for OSINT tool results"""
    def __init__(self):
        self.subdomains = set()
        self.emails = set()
        self.ips = set()
        self.social_profiles = set()

class OsintTool(ABC):
    """Abstract base class for OSINT tools"""
    def __init__(self, domain: str):
        self.domain = domain
        self.result = OsintToolResult()
    
    @abstractmethod
    async def execute(self) -> OsintToolResult:
        """Execute the tool and return results"""
        pass
    
    def get_name(self) -> str:
        """Get the name of the tool"""
        return self.__class__.__name__

class TheHarvesterTool(OsintTool):
    """TheHarvester implementation"""
    async def execute(self) -> OsintToolResult:
        logger.info(f"Running theHarvester against {self.domain}")
        try:
            # Run theHarvester with common sources
            sources = "bing,google,yahoo,baidu,duckduckgo,linkedin,twitter,hunter"
            cmd = [
                "python3", 
                "/opt/theHarvester/theHarvester.py", 
                "-d", self.domain,
                "-b", sources,
                "-f", f"/tmp/{self.domain}_theharvester"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"theHarvester failed: {stderr.decode()}")
                return self.result
                
            # Parse the output for useful information
            output = stdout.decode()
            
            # Extract subdomains
            subdomain_pattern = re.compile(r'(\w+\.)+' + re.escape(self.domain))
            for line in output.splitlines():
                matches = subdomain_pattern.findall(line)
                for match in matches:
                    if match.endswith(f".{self.domain}"):
                        self.result.subdomains.add(match)
            
            # Extract emails
            email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.' + re.escape(self.domain.split('.')[-2]) + r'\.' + re.escape(self.domain.split('.')[-1]))
            for line in output.splitlines():
                matches = email_pattern.findall(line)
                for match in matches:
                    self.result.emails.add(match)
            
            # Parse JSON output if available
            json_file = f"/tmp/{self.domain}_theharvester.json"
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if "hosts" in data:
                    for host in data["hosts"]:
                        # Extract IP and hostname
                        if "ip" in host and "hostname" in host:
                            self.result.ips.add(host["ip"])
                            self.result.subdomains.add(host["hostname"])
                
                if "emails" in data:
                    for email in data["emails"]:
                        self.result.emails.add(email)
            
            logger.info(f"theHarvester found {len(self.result.subdomains)} subdomains, {len(self.result.emails)} emails")
            return self.result
            
        except Exception as e:
            logger.error(f"Error running theHarvester: {str(e)}")
            return self.result

class AmassTool(OsintTool):
    """Amass implementation"""
    async def execute(self) -> OsintToolResult:
        logger.info(f"Running Amass against {self.domain}")
        try:
            # Run Amass enum with default settings
            output_file = f"/tmp/{self.domain}_amass.txt"
            cmd = [
                "amass",
                "enum",
                "-d", self.domain,
                "-o", output_file
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Amass failed: {stderr.decode()}")
                return self.result
            
            # Read output file and extract subdomains
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    for line in f:
                        subdomain = line.strip()
                        if subdomain:
                            self.result.subdomains.add(subdomain)
                
                # Try to resolve IPs for the found subdomains
                for subdomain in list(self.result.subdomains):
                    try:
                        ip = socket.gethostbyname(subdomain)
                        self.result.ips.add(ip)
                    except socket.gaierror:
                        pass
            
            logger.info(f"Amass found {len(self.result.subdomains)} subdomains, {len(self.result.ips)} IPs")
            return self.result
            
        except Exception as e:
            logger.error(f"Error running Amass: {str(e)}")
            return self.result

# Strategy pattern for tool execution
class ScanStrategy:
    """Strategy for executing different OSINT tools"""
    def __init__(self, tools: List[OsintTool]):
        self.tools = tools
    
    async def execute(self) -> Dict[str, Any]:
        """Execute all tools concurrently and merge results"""
        start_time = datetime.now().isoformat()
        
        # Create a unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Run all tools concurrently
        tasks = [tool.execute() for tool in self.tools]
        tool_results = await asyncio.gather(*tasks)
        
        # Merge results
        merged_result = self._merge_results(tool_results)
        
        end_time = datetime.now().isoformat()
        
        # Prepare the scan result
        scan_result = {
            "id": scan_id,
            "domain": self.tools[0].domain if self.tools else "",
            "startTime": start_time,
            "endTime": end_time,
            "summary": {
                "subdomains": len(merged_result["subdomains"]),
                "emails": len(merged_result["emails"]),
                "ips": len(merged_result["ips"]),
                "socialProfiles": len(merged_result["social_profiles"])
            },
            "details": merged_result
        }
        
        # Update the scan results in storage
        update_scan_results(scan_id, scan_result)
        
        return {"scanId": scan_id}
    
    def _merge_results(self, tool_results: List[OsintToolResult]) -> Dict[str, List[str]]:
        """Merge the results from multiple tools, removing duplicates"""
        merged = {
            "subdomains": [],
            "emails": [],
            "ips": [],
            "social_profiles": []
        }
        
        # Collect all unique findings
        all_subdomains = set()
        all_emails = set()
        all_ips = set()
        all_social_profiles = set()
        
        for result in tool_results:
            all_subdomains.update(result.subdomains)
            all_emails.update(result.emails)
            all_ips.update(result.ips)
            all_social_profiles.update(result.social_profiles)
        
        # Convert back to sorted lists
        merged["subdomains"] = sorted(list(all_subdomains))
        merged["emails"] = sorted(list(all_emails))
        merged["ips"] = sorted(list(all_ips))
        merged["social_profiles"] = sorted(list(all_social_profiles))
        
        return merged

# Factory for creating tool instances
class OsintToolFactory:
    """Factory for creating OSINT tool instances"""
    @staticmethod
    def create_tools(domain: str, options: Optional[Dict[str, bool]] = None) -> List[OsintTool]:
        """Create tool instances based on options"""
        tools = []
        
        # Default to both tools if no options are provided
        if options is None:
            options = {
                "useTheHarvester": True,
                "useAmass": True
            }
        
        # Create the requested tools
        if options.get("useTheHarvester", False):
            tools.append(TheHarvesterTool(domain))
        
        if options.get("useAmass", False):
            tools.append(AmassTool(domain))
        
        return tools

# Main function to start a scan
async def start_scan(domain: str, options: Optional[Dict[str, bool]] = None) -> Dict[str, str]:
    """Start a scan with the specified tools"""
    # Create tools based on options
    tools = OsintToolFactory.create_tools(domain, options)
    
    if not tools:
        raise ValueError("No tools selected for the scan")
    
    # Create the scan strategy
    strategy = ScanStrategy(tools)
    
    # Execute the scan
    return await strategy.execute() 