# OSINT Scanner - Assignment Submission

## 🚀 Public Docker Deployment

**The application is publicly deployed on Docker Hub:**

- **Backend Image**: `talgellis/osint-app-backend:latest`
- **Frontend Image**: `talgellis/osint-app-frontend:latest`

### Pull and Run Commands:
```bash
# Pull the images
docker pull talgellis/osint-app-backend:latest
docker pull talgellis/osint-app-frontend:latest

# Run the complete application
git clone https://github.com/tal-gellis/osint-app.git
cd osint-app
docker-compose up
```

**Docker Hub URLs:**
- https://hub.docker.com/r/talgellis/osint-app-backend
- https://hub.docker.com/r/talgellis/osint-app-frontend

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

### Using Public Docker Images (Recommended)
1. Ensure Docker and Docker Compose are installed
2. Clone the repository: `git clone https://github.com/tal-gellis/osint-app.git`
3. Navigate to directory: `cd osint-app`
4. Run: `docker-compose up`
5. Access the application at http://localhost:5173

The `docker-compose.yml` automatically pulls the public images from Docker Hub.

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

## ✅ Assignment Requirements Met

### Functional Requirements
- ✅ Domain input with validation
- ✅ Parallel execution of theHarvester and Amass
- ✅ Result merging and deduplication
- ✅ Persistent storage with SQLite
- ✅ Responsive UI (≥1300px)
- ✅ Robust error handling
- ✅ Design patterns implemented (Strategy + Factory)

### Non-Functional Requirements
- ✅ JSON over HTTP API
- ✅ FastAPI backend (100% Python 3)
- ✅ Structured logging with scan IDs
- ✅ Docker deployment
- ✅ Security: Input validation, process isolation

### Deliverables
- ✅ Source code repository
- ✅ README.md with 3-command quickstart
- ✅ Docker assets (Dockerfile + docker-compose.yml)
- ✅ Public Docker images on registry
- ✅ Tests included (backend + frontend)

### Bonus
- ✅ Excel export functionality
- ✅ Modern React with TypeScript
- ✅ Production-ready multi-stage Docker builds 