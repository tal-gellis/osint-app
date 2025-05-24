# OSINT Scanner

A web application for performing Open Source Intelligence (OSINT) scans on domains. The application collects information about subdomains, email addresses, IP addresses, and social media profiles associated with a given domain.

## Public Docker Images

This application is available as public Docker images on Docker Hub:

- **Backend**: `talgellis/osint-app-backend:latest`
- **Frontend**: `talgellis/osint-app-frontend:latest`

Anyone can pull and run these images without credentials:

```bash
docker pull talgellis/osint-app-backend:latest
docker pull talgellis/osint-app-frontend:latest
```

## Project Overview & Scope

This tool provides security professionals and researchers with a simple interface to gather intelligence about domains through passive reconnaissance. It focuses on:

- **Domain Reconnaissance**: Discover subdomains, IP addresses, and digital footprint
- **Email Harvesting**: Find email addresses associated with the target domain  
- **Social Media Presence**: Detect social media profiles linked to the domain
- **Concurrent Scanning**: Run theHarvester and Amass tools in parallel for efficiency
- **Data Persistence**: Store scan history with SQLite for future reference
- **Data Export**: Generate Excel reports with detailed findings

The application is designed for security assessments, competitive analysis, and cybersecurity research, all through a clean and intuitive interface.

## Features

- Domain scanning with real-time results
- Parallel execution of multiple OSINT tools (theHarvester and Amass)
- Persisted scan results using SQLite
- Merging and deduplication of results from multiple tools
- Responsive interface built with React and TypeScript
- Excel export functionality
- Dockerized deployment
- Robust error handling and structured logging

## Quick Start (3 Commands)

### Option 1: Using Public Docker Images (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/tal-gellis/osint-app.git && cd osint-app

# 2. Pull the public images (optional - docker-compose will pull automatically)
docker pull talgellis/osint-app-backend:latest && docker pull talgellis/osint-app-frontend:latest

# 3. Start the application
docker-compose up
```

### Option 2: Build from Source
```bash
# 1. Clone the repository
git clone https://github.com/tal-gellis/osint-app.git && cd osint-app

# 2. Build the containers
docker-compose build

# 3. Start the application
docker-compose up
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Architecture

The application follows a client-server architecture:

- **Backend:** FastAPI (Python 3)
  - Implements Strategy pattern for tool execution
  - Factory pattern for tool creation
  - SQLite for data persistence
  - Async processing using asyncio
  - Structured JSON logging

- **Frontend:** React with TypeScript
  - Clean, responsive UI
  - Real-time updates of scan status
  - Card-based result display
  - Modal dialogs for detailed views

## Tests

This project includes comprehensive test suites for both backend and frontend:

### Backend Tests
- **API Tests**: Test endpoints for scan creation, retrieval, and error handling
- **Worker Tests**: Verify parallel execution of OSINT tools and result merging
- **Storage Tests**: Validate data persistence and retrieval functionality

To run backend tests:
```bash
cd backend
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

### Frontend Tests
- **Component Tests**: Validate rendering and behavior of UI components
  - **ScanForm**: Tests form rendering, input validation, and submission
  - **ScanResultCard**: Tests result display, details expansion, and export

To run frontend tests:
```bash
cd frontend
npm install
npm test
```

More detailed testing information can be found in `backend/tests/README.md`.

## Development Mode

If you want to run the services individually during development:

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