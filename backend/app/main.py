"""
Main FastAPI application for AI-Powered Mock Interview System.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.auth import auth_router
from app.core.config import settings
from app.database.mongodb import mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("Starting up...")
    try:
        await mongodb.connect()
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Server will continue without MongoDB")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    try:
        await mongodb.disconnect()
    except Exception as e:
        print(f"MongoDB disconnect error: {e}")


app = FastAPI(
    title="AI-Powered Mock Interview API",
    description="API for AI-powered mock interview system using LLMs and RAG",
    version="0.1.0",
    lifespan=lifespan,
)

# Set up CORS middleware
if settings.DEBUG:
    # In development, allow all origins for easier testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # In production, use configured origins
    cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    db_status = "connected" if mongodb.client else "disconnected"
    return {
        "message": "Welcome to AI-Powered Mock Interview API",
        "version": "0.1.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "database": "MongoDB",
        "database_status": db_status,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    db_status = "connected" if mongodb.client else "disconnected"
    return {
        "status": "healthy",
        "database": "MongoDB",
        "database_status": db_status,
    }


@app.get("/database/test")
async def test_database_connection():
    """Test database connection endpoint."""
    try:
        if mongodb.client:
            # Ping the database
            await mongodb.client.admin.command('ping')
            return {
                "status": "success",
                "message": "Database connection successful",
                "database": settings.MONGODB_DB_NAME,
            }
        else:
            return {
                "status": "error",
                "message": "Database not connected",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
        }