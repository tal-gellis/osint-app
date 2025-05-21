import pytest
import asyncio
from workers import (
    TheHarvesterStrategy, 
    AmassStrategy, 
    run_tools_async,
    merge_results
)

async def test_the_harvester_strategy():
    """Test TheHarvesterStrategy executes and returns data"""
    scan_id = "test-scan-1"
    domain = "example.com"
    
    # Create and execute TheHarvester strategy
    harvester = TheHarvesterStrategy(scan_id, domain)
    result = await harvester.execute()
    
    # Check that basic structure is correct
    assert "subdomains" in result
    assert "emails" in result
    assert isinstance(result["subdomains"], list)
    assert isinstance(result["emails"], list)

async def test_amass_strategy():
    """Test AmassStrategy executes and returns data"""
    scan_id = "test-scan-1"
    domain = "example.com"
    
    # Create and execute Amass strategy
    amass = AmassStrategy(scan_id, domain)
    result = await amass.execute()
    
    # Check that basic structure is correct
    assert "subdomains" in result
    assert "ips" in result
    assert isinstance(result["subdomains"], list)
    assert isinstance(result["ips"], list)

async def test_merge_results():
    """Test results merging and deduplication"""
    # Sample results with duplicate data
    results = [
        {
            "subdomains": ["sub1.example.com", "sub2.example.com"],
            "emails": ["admin@example.com"]
        },
        {
            "subdomains": ["sub2.example.com", "sub3.example.com"],
            "ips": ["1.1.1.1"]
        }
    ]
    
    # Merge the results
    merged = await merge_results(results)
    
    # Check deduplication worked correctly
    assert len(merged["subdomains"]) == 3  # Duplicates removed
    assert "sub1.example.com" in merged["subdomains"]
    assert "sub2.example.com" in merged["subdomains"]
    assert "sub3.example.com" in merged["subdomains"] 