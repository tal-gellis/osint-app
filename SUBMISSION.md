# OSINT Scanner - Assignment Submission

## Project Overview

This project is a full-stack web application for performing Open Source Intelligence (OSINT) scans on domains. It allows users to scan domains to discover:
- Subdomains
- Email addresses
- IP addresses
- Social media profiles

## Technology Stack

### Backend
- FastAPI (Python 3.11)
- SQLite database for persistence
- Asyncio for concurrent processing
- Structured logging

### Frontend
- React with TypeScript
- Vite for fast development and building
- Custom hooks for state management
- Responsive design

### Deployment
- Docker and Docker Compose for containerization
- Nginx for serving the frontend and proxying API requests
- Multi-stage builds for optimized images

## How to Run the Project

### Using Docker (Recommended)
1. Ensure Docker and Docker Compose are installed
2. Clone the repository
3. Run `docker-compose up`
4. Access the application at http://localhost:5173

### Manual Development Setup
1. Start the backend:
   ```
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. Start the frontend:
   ```
   cd frontend
   npm install
   npm run dev
   ```

3. Access the application at http://localhost:5173

## Features Implemented

- Domain scanning interface
- Real-time scan status updates
- Results view with expandable cards
- Excel export functionality
- API error handling
- Persistent storage of scan results

## Design Patterns Used

- Strategy Pattern for OSINT tool implementation
- Factory Pattern for tool creation
- Repository Pattern for data access

## Security Considerations

- Input validation to prevent command injection
- Process isolation for tool execution
- CORS configuration for secure API access

## Screenshots

(Include screenshots of the application here)

## Future Enhancements

- Add more OSINT tools
- User authentication
- Scan comparison feature
- PDF report generation
- Email notifications 