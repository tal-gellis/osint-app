import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from workers import (
    TheHarvesterStrategy, 
    AmassStrategy, 
    SocialProfilesStrategy,
    ScanToolsFactory,
    merge_results,
    run_tools_async
)

# Test the Strategy Pattern implementations
async def test_the_harvester_strategy():
    """Test TheHarvesterStrategy executes and returns expected data"""
    scan_id = "test-scan-1"
    domain = "example.com"
    
    harvester = TheHarvesterStrategy(scan_id, domain)
    result = await harvester.execute()
    
    # Check that result has expected format
    assert "subdomains" in result
    assert "emails" in result
    assert isinstance(result["subdomains"], list)
    assert isinstance(result["emails"], list)
    
    # In the mocked version, we should have some predefined subdomains and emails
    assert len(result["subdomains"]) > 0
    assert len(result["emails"]) > 0

async def test_amass_strategy():
    """Test AmassStrategy executes and returns expected data"""
    scan_id = "test-scan-1"
    domain = "example.com"
    
    amass = AmassStrategy(scan_id, domain)
    result = await amass.execute()
    
    # Check that result has expected format
    assert "subdomains" in result
    assert "ips" in result
    assert isinstance(result["subdomains"], list)
    assert isinstance(result["ips"], list)
    
    # In the mocked version, we should have some predefined subdomains and IPs
    assert len(result["subdomains"]) > 0
    assert len(result["ips"]) > 0

# Test the Factory Pattern
def test_scan_tools_factory():
    """Test the factory creates the appropriate tools"""
    scan_id = "test-scan-1"
    domain = "example.com"
    
    tools = ScanToolsFactory.create_tools(scan_id, domain)
    
    # Should have created 3 tools (TheHarvester, Amass, SocialProfiles)
    assert len(tools) == 3
    assert isinstance(tools[0], TheHarvesterStrategy)
    assert isinstance(tools[1], AmassStrategy)
    assert isinstance(tools[2], SocialProfilesStrategy)
    
    # All tools should have the same scan_id and domain
    for tool in tools:
        assert tool.scan_id == scan_id
        assert tool.domain == domain

# Test result merging and deduplication
async def test_merge_results():
    """Test merging and deduplication of results"""
    # Create sample results with some overlapping data
    results_list = [
        {
            "subdomains": ["sub1.example.com", "sub2.example.com"],
            "emails": ["admin@example.com", "info@example.com"]
        },
        {
            "subdomains": ["sub2.example.com", "sub3.example.com"],
            "ips": ["1.1.1.1", "2.2.2.2"]
        },
        {
            "social_profiles": ["https://twitter.com/example"],
            "emails": ["info@example.com", "sales@example.com"]
        }
    ]
    
    merged = await merge_results(results_list)
    
    # Check deduplication worked - no duplicates in results
    assert len(merged["subdomains"]) == 3
    assert "sub1.example.com" in merged["subdomains"]
    assert "sub2.example.com" in merged["subdomains"]
    assert "sub3.example.com" in merged["subdomains"]
    
    assert len(merged["emails"]) == 3
    assert "admin@example.com" in merged["emails"]
    assert "info@example.com" in merged["emails"]
    assert "sales@example.com" in merged["emails"]
    
    assert len(merged["ips"]) == 2
    assert "1.1.1.1" in merged["ips"]
    assert "2.2.2.2" in merged["ips"]
    
    assert len(merged["social_profiles"]) == 1
    assert "https://twitter.com/example" in merged["social_profiles"]

# Test parallel execution
@patch('workers.ScanToolsFactory.create_tools')
async def test_parallel_execution(mock_create_tools):
    """Test that tools are executed in parallel"""
    scan_id = "test-scan-1"
    domain = "example.com"
    
    # Create mock tools with execute methods that we can track
    mock_harvester = AsyncMock()
    mock_harvester.execute = AsyncMock(return_value={"subdomains": ["sub1.example.com"], "emails": ["admin@example.com"]})
    
    mock_amass = AsyncMock()
    mock_amass.execute = AsyncMock(return_value={"subdomains": ["sub2.example.com"], "ips": ["1.1.1.1"]})
    
    # Configure the factory to return our mock tools
    mock_create_tools.return_value = [mock_harvester, mock_amass]
    
    # Run the tools
    result = await run_tools_async(scan_id, domain)
    
    # Verify both tool execute methods were called exactly once
    mock_harvester.execute.assert_called_once()
    mock_amass.execute.assert_called_once()
    
    # Verify the result contains merged data from both tools
    assert "sub1.example.com" in result["subdomains"]
    assert "sub2.example.com" in result["subdomains"]
    assert "admin@example.com" in result["emails"]
    assert "1.1.1.1" in result["ips"] 