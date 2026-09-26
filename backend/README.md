# Backend - AI-Powered Mock Interview System

FastAPI backend for the AI-powered mock interview platform.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

The `.env` file is already created with basic configuration:
- Server runs on port 8000
- CORS configured for localhost:3000 (frontend) and localhost:8000

### 3. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Welcome message and API info
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── core/
│   └── config.py       # Application configuration
├── api/
│   └── v1/
│       ├── api.py      # API router (version 1)
│       └── endpoints/  # API endpoint modules
├── models/             # Data models (for future use)
├── services/           # Business services (for future use)
└── utils/              # Utility functions (for future use)
```

## Dependencies

- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `pydantic-settings==2.1.0` - Settings management
- `python-dotenv==1.0.0` - Environment variables

## Development Notes

- Server runs at: http://localhost:8000
- Auto-reload on code changes
- CORS configured for frontend development
- No authentication, database, or AI functionality implemented yet