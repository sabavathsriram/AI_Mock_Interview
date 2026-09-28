#!/usr/bin/env python
"""
Entry point for running the backend server.
Ensures .env file is loaded before starting the app.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Load .env BEFORE importing any app modules
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from {env_path}")

# Now we can import and run uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
