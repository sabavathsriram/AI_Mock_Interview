#!/usr/bin/env python3
"""
Test the endpoint and check all response details.
"""

import asyncio
import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import sys
sys.path.insert(0, "backend")

from app.auth.jwt import JWTManager

async def main():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    sessions_collection = db["interview_sessions"]
    
    # Find a completed session with responses
    session = await sessions_collection.find_one({
        "status": "completed",
        "responses": {"$ne": []}
    })
    
    if not session:
        print("No completed sessions with responses found")
        return
    
    session_id = str(session["_id"])
    user_id = session["user_id"]
    
    # Create a JWT token for the user
    token = JWTManager.create_access_token({"sub": user_id})
    
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}")
    print(f"Token: {token[:50]}...")
    
    print(f"\n[TEST] Calling POST /evaluate-all with auth token...")
    
    try:
        response = requests.post(
            f"http://localhost:8080/api/v1/interviews/{session_id}/evaluate-all",
            headers={"Authorization": f"Bearer {token}"},
            json={},
            timeout=180
        )
        print(f"\nStatus Code: {response.status_code}")
        print(f"Status Text: {response.reason}")
        
        print(f"\nHeaders:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
        
        print(f"\nResponse Body:")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text[:500])
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
