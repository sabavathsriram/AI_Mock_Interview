#!/usr/bin/env python3
"""
Debug script to test the Prompt 12 evaluation flow end-to-end.

This script:
1. Connects to MongoDB
2. Finds a completed interview session
3. Inspects the response structure
4. Calls the /evaluate-all endpoint
5. Checks if evaluations were persisted
"""

import asyncio
import json
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import requests
from datetime import datetime

# MongoDB connection
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "mock_interview_db"

# Backend API
API_URL = "http://localhost:8080"
TOKEN = ""  # Will need to be set via environment

async def connect_mongodb():
    """Connect to MongoDB."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    return db

async def inspect_session_structure(db, session_id):
    """Inspect the structure of a session and its responses."""
    print(f"\n=== INSPECTING SESSION STRUCTURE ===")
    print(f"Session ID: {session_id}")
    
    sessions_collection = db["interview_sessions"]
    
    try:
        session_doc = await sessions_collection.find_one({
            "_id": ObjectId(session_id)
        })
        
        if not session_doc:
            print(f"ERROR: Session {session_id} not found")
            return None
        
        print(f"\nSession Status: {session_doc.get('status')}")
        print(f"Interview Type: {session_doc.get('interview_type')}")
        print(f"Difficulty Level: {session_doc.get('difficulty_level')}")
        print(f"Total Responses: {len(session_doc.get('responses', []))}")
        
        # Check responses
        responses = session_doc.get('responses', [])
        if responses:
            print(f"\n--- RESPONSES DETAIL ---")
            for idx, resp in enumerate(responses):
                print(f"\nResponse {idx+1}:")
                print(f"  Response ID: {resp.get('response_id')}")
                print(f"  Question ID: {resp.get('question_id')}")
                print(f"  Answer (first 100 chars): {resp.get('answer', '')[:100]}")
                print(f"  Evaluation: {resp.get('evaluation')}")
                print(f"  Has evaluation: {'evaluation' in resp and resp['evaluation'] is not None}")
        
        return session_doc
        
    except Exception as e:
        print(f"ERROR inspecting session: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def find_completed_session(db):
    """Find a completed interview session."""
    sessions_collection = db["interview_sessions"]
    
    # Find a completed session with responses
    session = await sessions_collection.find_one({
        "status": "completed",
        "responses": {"$ne": []}
    })
    
    if session:
        return str(session["_id"])
    
    # If no completed session, find any session with responses
    session = await sessions_collection.find_one({
        "responses": {"$ne": []}
    })
    
    if session:
        print(f"Found session with status: {session.get('status')}")
        return str(session["_id"])
    
    return None

def call_evaluate_all_endpoint(session_id, user_id, token):
    """Call the /evaluate-all endpoint."""
    print(f"\n=== CALLING /evaluate-all ENDPOINT ===")
    
    url = f"{API_URL}/api/v1/interviews/{session_id}/evaluate-all"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"URL: {url}")
    print(f"Token: {token[:20]}..." if token else "NO TOKEN")
    
    try:
        response = requests.post(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"ERROR: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR calling endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def check_evaluations_after(db, session_id):
    """Check if evaluations were persisted after the call."""
    print(f"\n=== CHECKING EVALUATIONS AFTER ===")
    
    sessions_collection = db["interview_sessions"]
    
    session_doc = await sessions_collection.find_one({
        "_id": ObjectId(session_id)
    })
    
    if not session_doc:
        print("ERROR: Session not found after evaluation")
        return
    
    responses = session_doc.get('responses', [])
    evaluated_count = len([r for r in responses if r.get('evaluation') is not None])
    
    print(f"Total Responses: {len(responses)}")
    print(f"Evaluated Responses: {evaluated_count}")
    
    if evaluated_count > 0:
        print(f"\n✓ SUCCESS: Evaluations are persisted!")
        for idx, resp in enumerate(responses):
            if resp.get('evaluation'):
                print(f"\nResponse {idx+1} Evaluation:")
                print(f"  Overall Score: {resp['evaluation'].get('overall_score')}/10")
                print(f"  Strengths: {resp['evaluation'].get('strengths', [])[:2]}")
                print(f"  Weaknesses: {resp['evaluation'].get('weaknesses', [])[:2]}")
    else:
        print(f"\n✗ PROBLEM: No evaluations found after calling endpoint")

async def main():
    """Main function."""
    print("=".* 60)
    print("PROMPT 12 EVALUATION FLOW DEBUG")
    print("=" * 60)
    
    # Get token from environment
    import os
    token = os.getenv("TEST_TOKEN")
    if not token:
        print("\nERROR: TEST_TOKEN not set in environment")
        print("Set with: $env:TEST_TOKEN='your-token'")
        sys.exit(1)
    
    # Connect to MongoDB
    db = await connect_mongodb()
    print(f"\n✓ Connected to MongoDB: {DB_NAME}")
    
    # Find a session
    session_id = await find_completed_session(db)
    if not session_id:
        print("\nERROR: No interview sessions found")
        sys.exit(1)
    
    print(f"✓ Found session: {session_id}")
    
    # Inspect before
    session_doc = await inspect_session_structure(db, session_id)
    if not session_doc:
        sys.exit(1)
    
    user_id = session_doc.get('user_id')
    
    # Call endpoint
    result = call_evaluate_all_endpoint(session_id, user_id, token)
    
    if result:
        print(f"\nEndpoint Response:")
        print(json.dumps(result, indent=2))
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Check after
    await check_evaluations_after(db, session_id)
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
