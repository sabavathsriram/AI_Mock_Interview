#!/usr/bin/env python3
"""STEP 1: Inspect the real session and responses"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def inspect_session():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    sessions_collection = db["interview_sessions"]
    
    session_id = "6abac2656bf37c60649a2a2d"
    
    session_doc = await sessions_collection.find_one({
        "_id": ObjectId(session_id)
    })
    
    if not session_doc:
        print("SESSION NOT FOUND")
        return
    
    print("=" * 70)
    print("STEP 1: REAL SESSION INSPECTION")
    print("=" * 70)
    print(f"Session ID: {session_id}")
    print(f"Status: {session_doc.get('status')}")
    print(f"Interview Plan ID: {session_doc.get('interview_plan_id')}")
    print(f"Total responses: {len(session_doc.get('responses', []))}\n")
    
    print("RESPONSES DETAIL:")
    print("-" * 70)
    
    for idx, resp in enumerate(session_doc.get('responses', [])):
        print(f"\n[Response {idx+1}]")
        print(f"  response_id: {resp.get('response_id')}")
        print(f"  question_id: {resp.get('question_id')}")
        print(f"  answer: {resp.get('answer', '')[:100]}")
        print(f"  has evaluation field: {'evaluation' in resp}")
        print(f"  evaluation is None: {resp.get('evaluation') is None}")
    
    client.close()

asyncio.run(inspect_session())
