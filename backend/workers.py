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
import re
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_subdomains(domain: str) -> list:
    """Get subdomains using dns.resolver"""
    subdomains = set()
    try:
        # Common subdomain prefixes
        prefixes = ['www', 'mail', 'ftp', 'smtp', 'pop', 'api', 'dev', 'staging', 'test']
        for prefix in prefixes:
            try:
                subdomain = f"{prefix}.{domain}"
                socket.gethostbyname(subdomain)
                subdomains.add(subdomain)
            except socket.gaierror:
                continue
    except Exception as e:
        print(f"Error getting subdomains: {e}")
    return list(subdomains)

def get_emails(domain: str) -> list:
    """Get email addresses from WHOIS and website"""
    emails = set()
    try:
        # Try to get WHOIS information
        whois_cmd = f"whois {domain}"
        result = subprocess.run(whois_cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            # Simple email regex pattern
            import re
            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
            found_emails = re.findall(email_pattern, result.stdout)
            emails.update(found_emails)
    except Exception as e:
        print(f"Error getting emails: {e}")
    return list(emails)

def get_ips(domain: str) -> list:
    """Get IP addresses for domain and subdomains"""
    ips = set()
    try:
        # Get IP for main domain
        ip = socket.gethostbyname(domain)
        ips.add(ip)
        
        # Get IPs for subdomains
        subdomains = get_subdomains(domain)
        for subdomain in subdomains:
            try:
                ip = socket.gethostbyname(subdomain)
                ips.add(ip)
            except socket.gaierror:
                continue
    except Exception as e:
        print(f"Error getting IPs: {e}")
    return list(ips)

def get_social_profiles(domain: str) -> list:
    """Get social media profiles"""
    profiles = []
    try:
        # Try to get website content
        response = requests.get(f"https://{domain}", timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for social media links
            social_domains = ['twitter.com', 'linkedin.com', 'facebook.com', 'instagram.com']
            for link in soup.find_all('a', href=True):
                href = link['href']
                for social_domain in social_domains:
                    if social_domain in href:
                        profiles.append(href)
    except Exception as e:
        print(f"Error getting social profiles: {e}")
    return profiles

class ToolStrategy:
    """Strategy pattern for running different OSINT tools"""
    def __init__(self, scan_id, domain):
        self.scan_id = scan_id
        self.domain = domain
        
    async def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")


class TheHarvesterStrategy(ToolStrategy):
    """Strategy for running theHarvester"""
    async def execute(self):
        logger.info(json.dumps({
            "scan_id": self.scan_id,
            "tool": "theHarvester",
            "domain": self.domain,
            "status": "starting"
        }))
        
        try:
            # Use asyncio.create_subprocess_exec for safer process creation
            cmd = ["theHarvester", "-d", self.domain, "-b", "all"]
            
            # Simulate theHarvester results for development - REMOVE IN PRODUCTION
            await asyncio.sleep(4)  # Simulate tool running time
            
            # Simulated results - in production, parse the actual output
            subdomains = [f"mail.{self.domain}", f"www.{self.domain}", f"dev.{self.domain}"]
            emails = [f"admin@{self.domain}", f"info@{self.domain}"]
            
            logger.info(json.dumps({
                "scan_id": self.scan_id,
                "tool": "theHarvester",
                "domain": self.domain,
                "status": "completed",
                "subdomains_found": len(subdomains),
                "emails_found": len(emails)
            }))
            
            return {
                "subdomains": subdomains,
                "emails": emails
            }
        except Exception as e:
            logger.error(json.dumps({
                "scan_id": self.scan_id,
                "tool": "theHarvester",
                "domain": self.domain,
                "status": "error",
                "error": str(e)
            }))
            return {"error": str(e)}


class AmassStrategy(ToolStrategy):
    """Strategy for running Amass"""
    async def execute(self):
        logger.info(json.dumps({
            "scan_id": self.scan_id,
            "tool": "Amass",
            "domain": self.domain,
            "status": "starting"
        }))
        
        try:
            # Use asyncio.create_subprocess_exec for safer process creation
            cmd = ["amass", "enum", "-d", self.domain, "-passive"]
            
            # Simulate Amass results for development - REMOVE IN PRODUCTION
            await asyncio.sleep(5)  # Simulate tool running time
            
            # Simulated results - in production, parse the actual output
            subdomains = [f"api.{self.domain}", f"blog.{self.domain}", f"store.{self.domain}"]
            ips = ["192.168.1.1", "10.0.0.1"]
            
            logger.info(json.dumps({
                "scan_id": self.scan_id,
                "tool": "Amass",
                "domain": self.domain,
                "status": "completed",
                "subdomains_found": len(subdomains),
                "ips_found": len(ips)
            }))
            
            return {
                "subdomains": subdomains,
                "ips": ips
            }
        except Exception as e:
            logger.error(json.dumps({
                "scan_id": self.scan_id,
                "tool": "Amass",
                "domain": self.domain,
                "status": "error",
                "error": str(e)
            }))
            return {"error": str(e)}


class SocialProfilesStrategy(ToolStrategy):
    """Strategy for finding social profiles"""
    async def execute(self):
        logger.info(json.dumps({
            "scan_id": self.scan_id,
            "tool": "SocialProfilesFinder",
            "domain": self.domain,
            "status": "starting"
        }))
        
        try:
            # Simulate finding social profiles
            await asyncio.sleep(3)
            
            # Simulated results
            profiles = [
                f"https://twitter.com/{self.domain.split('.')[0]}",
                f"https://linkedin.com/company/{self.domain.split('.')[0]}",
                f"https://facebook.com/{self.domain.split('.')[0]}"
            ]
            
            logger.info(json.dumps({
                "scan_id": self.scan_id,
                "tool": "SocialProfilesFinder",
                "domain": self.domain,
                "status": "completed",
                "profiles_found": len(profiles)
            }))
            
            return {
                "social_profiles": profiles
            }
        except Exception as e:
            logger.error(json.dumps({
                "scan_id": self.scan_id,
                "tool": "SocialProfilesFinder",
                "domain": self.domain,
                "status": "error",
                "error": str(e)
            }))
            return {"error": str(e)}


class ScanToolsFactory:
    """Factory pattern for creating OSINT tool strategies"""
    @staticmethod
    def create_tools(scan_id, domain):
        return [
            TheHarvesterStrategy(scan_id, domain),
            AmassStrategy(scan_id, domain),
            SocialProfilesStrategy(scan_id, domain)
        ]


async def merge_results(results_list):
    """Merge and deduplicate results from multiple tools"""
    merged = {
        "subdomains": set(),
        "emails": set(),
        "ips": set(),
        "social_profiles": set(),
        "errors": []
    }
    
    for result in results_list:
        if "error" in result:
            merged["errors"].append(result["error"])
            continue
            
        # Merge subdomains
        if "subdomains" in result:
            merged["subdomains"].update(result["subdomains"])
        
        # Merge emails
        if "emails" in result:
            merged["emails"].update(result["emails"])
        
        # Merge IPs
        if "ips" in result:
            merged["ips"].update(result["ips"])
        
        # Merge social profiles
        if "social_profiles" in result:
            merged["social_profiles"].update(result["social_profiles"])
    
    # Convert sets to lists for JSON serialization
    return {
        "subdomains": list(merged["subdomains"]),
        "emails": list(merged["emails"]),
        "ips": list(merged["ips"]),
        "social_profiles": list(merged["social_profiles"]),
        "errors": merged["errors"]
    }


async def run_tools_async(scan_id, domain):
    """Run all OSINT tools in parallel using asyncio"""
    tools = ScanToolsFactory.create_tools(scan_id, domain)
    
    # Run all tools concurrently and gather results
    tasks = [tool.execute() for tool in tools]
    results = await asyncio.gather(*tasks)
    
    # Merge and deduplicate results
    return await merge_results(results)


def run_osint_scan(scan_id: str, domain: str, start_time: datetime):
    """Run OSINT scan on the given domain"""
    logger.info(json.dumps({
        "scan_id": scan_id,
        "domain": domain,
        "status": "started",
        "message": "Starting OSINT scan"
    }))
    
    try:
        # Create and run event loop for the async tasks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run tools in parallel and get merged results
        results = loop.run_until_complete(run_tools_async(scan_id, domain))
        loop.close()
        
        # Calculate end time
        end_time = datetime.utcnow()
        
        # Log scan completion
        logger.info(json.dumps({
            "scan_id": scan_id,
            "domain": domain,
            "status": "completed",
            "duration_seconds": (end_time - start_time).total_seconds(),
            "results_summary": {
                "subdomains": len(results["subdomains"]),
                "emails": len(results["emails"]),
                "ips": len(results["ips"]),
                "social_profiles": len(results["social_profiles"]),
                "errors": len(results["errors"])
            }
        }))
        
        # Update scan with results
        update_scan_results(scan_id, results, end_time)
    except Exception as e:
        logger.error(json.dumps({
            "scan_id": scan_id,
            "domain": domain,
            "status": "error",
            "error": str(e)
        }))
        
        # Update scan with error status
        error_results = {"error": str(e)}
        update_scan_results(scan_id, error_results, datetime.utcnow())

