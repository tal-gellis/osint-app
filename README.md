# OSINT Scanner

A web application for performing Open Source Intelligence (OSINT) scans on domains. The application collects information about subdomains, email addresses, IP addresses, and social media profiles associated with a given domain.

## Features

- Domain scanning with real-time results
- Parallel execution of multiple OSINT tools (theHarvester and Amass)
- Persisted scan results using SQLite
- Merging and deduplication of results from multiple tools
- Responsive interface built with React and Material UI
- Excel export functionality
- Dockerized deployment
- Robust error handling and structured logging

## Architecture

The application follows a client-server architecture:

- **Backend:** FastAPI (Python 3)
  - Implements Strategy pattern for tool execution
  - Factory pattern for tool creation
  - SQLite for data persistence
  - Async processing using asyncio
  - Structured JSON logging

- **Frontend:** React with TypeScript
  - Material UI components
  - Real-time updates of scan status
  - Responsive card-based UI
  - Modal dialogs for detailed views

## Quick Start

### Development Mode

1. Start the backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

2. Start the frontend:
```bash
cd frontend
npm install
npm start
```

### Docker Deployment

```bash
docker-compose up
```

## API Endpoints

- `POST /scan` - Start a new scan (accepts domain)
- `GET /scans` - List all scans
- `GET /scans/{scan_id}` - Get a specific scan
- `GET /export/{scan_id}` - Export scan results to Excel

## Design Patterns

1. **Strategy Pattern**: Implemented for executing different OSINT tools (TheHarvesterStrategy, AmassStrategy, etc.)
2. **Factory Pattern**: ScanToolsFactory creates appropriate tool strategies based on requirements

## Future Enhancements

- Add more OSINT tools (e.g., Shodan, Censys)
- Implement authenticated user sessions
- Add scan result comparison feature
- Include vulnerability scanning

## Security Considerations

- Input validation to prevent command injection
- Process isolation for tool execution
- Structured error handling
- Rate limiting and concurrency control

## License

MIT License 