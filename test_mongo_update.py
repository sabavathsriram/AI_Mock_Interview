#!/usr/bin/env python3
"""
Test MongoDB update operation with positional operator.
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
    
    session_id = session['_id']
    first_response_id = session['responses'][0]['response_id']
    
    print(f"Session ID: {session_id}")
    print(f"Response ID to update: {first_response_id}")
    
    # Create test evaluation
    test_evaluation = {
        "correctness": 7,
        "relevance": 8,
        "technical_depth": 6,
        "clarity": 8,
        "reasoning": 7,
        "communication": 8,
        "overall_score": 7,
        "strengths": ["Good explanation", "Clear code example"],
        "weaknesses": ["Missing error handling"],
        "skills_demonstrated": ["JavaScript", "DOM manipulation", "Async programming"],
        "improvement_suggestions": ["Learn more about async/await patterns", "Add error handling"]
    }
    
    print(f"\n=== BEFORE UPDATE ===")
    session_before = await sessions_collection.find_one({"_id": session_id})
    print(f"First response has evaluation: {'evaluation' in session_before['responses'][0]}")
    
    print(f"\n=== PERFORMING UPDATE ===")
    # Try the update
    result = await sessions_collection.find_one_and_update(
        {
            "_id": session_id,
            "responses.response_id": first_response_id
        },
        {
            "$set": {
                "responses.$.evaluation": test_evaluation
            }
        }
    )
    
    if result:
        print(f"✓ Update successful")
        print(f"Matched document ID: {result['_id']}")
    else:
        print(f"✗ Update failed - no document matched")
        print(f"Query was: _id={session_id}, responses.response_id={first_response_id}")
    
    print(f"\n=== AFTER UPDATE ===")
    session_after = await sessions_collection.find_one({"_id": session_id})
    first_response_after = session_after['responses'][0]
    
    print(f"First response has evaluation: {'evaluation' in first_response_after}")
    if 'evaluation' in first_response_after:
        print(f"Evaluation overall_score: {first_response_after['evaluation'].get('overall_score')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
