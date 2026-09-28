#!/usr/bin/env python3
"""
Test the complete evaluation flow WITH proper authentication.
1. Create a JWT token for a test user
2. Use token to call /evaluate-all
3. Verify evaluations were stored
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
    
    print("=" * 60)
    print("TESTING WITH AUTHENTICATION")
    print("=" * 60)
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}")
    
    # Create a JWT token for the user
    token = JWTManager.create_access_token({"sub": user_id})
    print(f"Token created: {token[:50]}...")
    
    # Check evaluations before
    has_evals_before = len([r for r in session.get('responses', []) if r.get('evaluation') is not None])
    print(f"\nEvaluations before: {has_evals_before}")
    
    print(f"\n[TEST] Calling POST /evaluate-all with auth token...")
    
    try:
        response = requests.post(
            f"http://localhost:8080/api/v1/interviews/{session_id}/evaluate-all",
            headers={"Authorization": f"Bearer {token}"},
            json={},
            timeout=180  # Give it 3 minutes for Groq to respond
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"ERROR Response: {response.text[:500]}")
        else:
            result = response.json()
            print(f"Success Response: {json.dumps(result, indent=2)}")
    except requests.Timeout:
        print(f"ERROR: Request timed out (likely Groq API taking time)")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n[TEST] Checking MongoDB after call...")
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Check again
    session_after = await sessions_collection.find_one({"_id": ObjectId(session_id)})
    has_evals_after = len([r for r in session_after.get('responses', []) if r.get('evaluation') is not None])
    print(f"Evaluations after: {has_evals_after}")
    
    if has_evals_after > has_evals_before:
        print(f"\n[SUCCESS] {has_evals_after - has_evals_before} evaluations were stored!")
    else:
        print(f"\n[FAILURE] No evaluations were stored")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
