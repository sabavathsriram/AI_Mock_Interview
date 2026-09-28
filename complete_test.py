#!/usr/bin/env python3
"""
Complete end-to-end test of evaluation flow.
1. Find a completed interview with responses
2. Check if it has evaluations
3. Call the /evaluate-all endpoint via HTTP
4. Verify evaluations were stored
"""

import asyncio
import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def main():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    sessions_collection = db["interview_sessions"]
    
    # Find a completed session with responses and NO evaluations
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
    print("END-TO-END EVALUATION TEST")
    print("=" * 60)
    print(f"\nSession ID: {session_id}")
    print(f"User ID: {user_id}")
    print(f"Total responses: {len(session.get('responses', []))}")
    
    # Check evaluations before
    has_evaluations_before = len([r for r in session.get('responses', []) if r.get('evaluation') is not None])
    print(f"Evaluations before: {has_evaluations_before}")
    
    print(f"\n[STEP 1] Calling GET /evaluation to check current state...")
    
    # Get auth token (or skip if not available)
    # For now, let's try without auth
    try:
        response = requests.get(
            f"http://localhost:8080/api/v1/interviews/{session_id}/evaluation",
            headers={"Authorization": "Bearer test"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            eval_data = response.json()
            print(f"Overall score: {eval_data.get('overall_score')}")
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print(f"\n[STEP 2] Calling POST /evaluate-all endpoint...")
    
    try:
        response = requests.post(
            f"http://localhost:8080/api/v1/interviews/{session_id}/evaluate-all",
            headers={"Authorization": "Bearer test"},
            json={}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print(f"\n[STEP 3] Checking MongoDB after endpoint call...")
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Check evaluations after
    session_after = await sessions_collection.find_one({"_id": ObjectId(session_id)})
    has_evaluations_after = len([r for r in session_after.get('responses', []) if r.get('evaluation') is not None])
    print(f"Evaluations after: {has_evaluations_after}")
    
    if has_evaluations_after > has_evaluations_before:
        print(f"\n[SUCCESS] Evaluations were added: {has_evaluations_after - has_evaluations_before} new evaluations")
    else:
        print(f"\n[FAILURE] No new evaluations were added")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
