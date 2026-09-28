#!/usr/bin/env python3
"""
Direct MongoDB inspection script to check response structure.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import json

async def main():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    
    # Find a session with responses
    sessions_collection = db["interview_sessions"]
    
    session = await sessions_collection.find_one({
        "responses": {"$ne": []}
    })
    
    if not session:
        print("No sessions with responses found")
        return
    
    print(f"Session ID: {session['_id']}")
    print(f"Total responses: {len(session.get('responses', []))}")
    print(f"\n=== FIRST RESPONSE STRUCTURE ===")
    
    if session.get('responses'):
        first_response = session['responses'][0]
        print(f"Keys in response: {list(first_response.keys())}")
        print(f"\nFirst response (raw):")
        print(json.dumps(first_response, indent=2, default=str))
        
        # Check if response_id exists
        if 'response_id' in first_response:
            print(f"\n✓ response_id found: {first_response['response_id']}")
        else:
            print(f"\n✗ response_id NOT FOUND in response")
            print(f"Available keys: {list(first_response.keys())}")
        
        # Check if evaluation exists
        if 'evaluation' in first_response:
            print(f"✓ evaluation field exists: {first_response['evaluation'] is not None}")
        else:
            print(f"✗ evaluation field does not exist")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
