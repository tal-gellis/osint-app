# OSINT Scanner Tests

This directory contains tests for the OSINT Scanner backend.

## Test Structure

- `test_api.py` - Tests for API endpoints
- `test_workers.py` - Tests for OSINT tool execution and parallel processing
- `test_storage.py` - Tests for data storage functionality

## Running Tests

To run the tests, first install the required dependencies:

```bash
pip install pytest pytest-asyncio
```

Then run the tests from the backend directory:

```bash
cd backend
python -m pytest tests/ -v
```

## Test Coverage

These tests cover:

1. API Endpoints
   - Scan creation
   - Scan retrieval (single and all)
   - Error handling

2. Tool Execution
   - Individual tool strategies
   - Factory pattern
   - Parallel execution
   - Result merging and deduplication

3. Storage
   - Scan persistence
   - Result updates
   - Data retrieval 