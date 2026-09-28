#!/usr/bin/env python3
"""STEP 2: Call /evaluate-all endpoint with auth"""

import asyncio
import requests
import json
import sys
sys.path.insert(0, "backend")

from app.auth.jwt import JWTManager
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def call_endpoint():
    # Get user ID from session
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    session_doc = await db["interview_sessions"].find_one({
        "_id": ObjectId("6abac2656bf37c60649a2a2d")
    })
    
    user_id = session_doc["user_id"]
    token = JWTManager.create_access_token({"sub": user_id})
    
    print("=" * 70)
    print("STEP 2: CALL /evaluate-all ENDPOINT")
    print("=" * 70)
    print(f"Session ID: 6abac2656bf37c60649a2a2d")
    print(f"User ID: {user_id}")
    print(f"Token: {token[:50]}...")
    print()
    
    try:
        print("[CALLING] POST /api/v1/interviews/6abac2656bf37c60649a2a2d/evaluate-all")
        response = requests.post(
            "http://localhost:8080/api/v1/interviews/6abac2656bf37c60649a2a2d/evaluate-all",
            headers={"Authorization": f"Bearer {token}"},
            json={},
            timeout=300
        )
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Status Text: {response.reason}")
        print()
        
        data = response.json()
        print("RESPONSE JSON:")
        print(json.dumps(data, indent=2))
        print()
        
        print("KEY METRICS:")
        print(f"  total_responses: {data.get('total_responses')}")
        print(f"  evaluated_count: {data.get('evaluated_count')}")
        print(f"  newly_evaluated: {data.get('newly_evaluated')}")
        print(f"  message: {data.get('message')}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    client.close()

asyncio.run(call_endpoint())
