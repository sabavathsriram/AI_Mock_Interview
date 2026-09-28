#!/usr/bin/env python3
"""Test GET /evaluation endpoint"""

import asyncio
import requests
import json
import sys
sys.path.insert(0, "backend")

from app.auth.jwt import JWTManager
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def test():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    session_doc = await db["interview_sessions"].find_one({
        "_id": ObjectId("6abac2656bf37c60649a2a2d")
    })
    
    user_id = session_doc["user_id"]
    token = JWTManager.create_access_token({"sub": user_id})
    
    print("=" * 70)
    print("TEST: GET /evaluation ENDPOINT")
    print("=" * 70)
    
    response = requests.get(
        "http://localhost:8080/api/v1/interviews/6abac2656bf37c60649a2a2d/evaluation",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"HTTP Status: {response.status_code}\n")
    
    data = response.json()
    print(json.dumps(data, indent=2))
    
    print("\n" + "=" * 70)
    print("KEY SCORES:")
    print("=" * 70)
    print(f"overall_score: {data.get('overall_score')}")
    print(f"technical_knowledge_score: {data.get('technical_knowledge_score')}")
    print(f"communication_score: {data.get('communication_score')}")
    print(f"problem_solving_score: {data.get('problem_solving_score')}")
    print(f"is_ai_generated: {data.get('is_ai_generated')}")
    
    client.close()

asyncio.run(test())
