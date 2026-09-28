#!/usr/bin/env python3
"""
Check what responses are unevaluated in a session.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    sessions_collection = db["interview_sessions"]
    
    session_id = "6aba9bdd6d66f09b2cb8d1be"
    
    session = await sessions_collection.find_one({
        "_id": ObjectId(session_id)
    })
    
    if not session:
        print("Session not found")
        return
    
    print(f"Session: {session_id}")
    print(f"Status: {session.get('status')}")
    print(f"Total responses: {len(session.get('responses', []))}")
    
    print("\n=== RESPONSES ===")
    for idx, resp in enumerate(session.get('responses', [])):
        has_eval = resp.get('evaluation') is not None
        print(f"{idx+1}. Response ID: {resp.get('response_id')}, Has evaluation: {has_eval}")
    
    # Count unevaluated
    unevaluated = len([r for r in session.get('responses', []) if r.get('evaluation') is None])
    print(f"\nTotal unevaluated: {unevaluated}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
