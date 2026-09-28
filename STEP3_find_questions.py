#!/usr/bin/env python3
"""STEP 3: Find where the actual questions are stored"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def find_questions():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ai_mock_interview_db"]
    
    session_id = "6abac2656bf37c60649a2a2d"
    session_doc = await db["interview_sessions"].find_one({
        "_id": ObjectId(session_id)
    })
    
    print("=" * 70)
    print("STEP 3: FIND WHERE QUESTIONS ARE STORED")
    print("=" * 70)
    
    # Get the question IDs from responses
    question_ids = [r.get('question_id') for r in session_doc.get('responses', [])]
    print(f"\nQuestion IDs from responses:")
    for idx, qid in enumerate(question_ids, 1):
        print(f"  {idx}. {qid}")
    
    # Try to find these questions in different collections
    print("\n" + "-" * 70)
    print("SEARCHING IN COLLECTIONS:")
    print("-" * 70)
    
    # Search in interview_questions
    print("\n[1] Searching in 'interview_questions' collection...")
    interview_qs = db["interview_questions"]
    for qid in question_ids:
        try:
            q_doc = await interview_qs.find_one({"_id": ObjectId(qid)})
            if q_doc:
                print(f"  FOUND: {qid}")
                print(f"    question_text: {q_doc.get('question_text', '')[:80]}")
            else:
                print(f"  NOT FOUND: {qid}")
        except:
            print(f"  ERROR searching: {qid}")
    
    # Search in interview_plans
    print("\n[2] Searching in 'interview_plans' collection...")
    plans = db["interview_plans"]
    plan_count = await plans.count_documents({})
    print(f"  Total plans in DB: {plan_count}")
    
    # Check if any plan contains these questions
    for qid in question_ids[:1]:  # Check first question
        plan_with_q = await plans.find_one({"questions._id": ObjectId(qid)})
        if plan_with_q:
            print(f"  Found plan containing questions: {plan_with_q['_id']}")
            for q in plan_with_q.get('questions', []):
                if str(q.get('_id')) == qid:
                    print(f"    Question: {q.get('question_text', '')[:80]}")
        else:
            print(f"  No plan found containing question: {qid}")
    
    # Search in session's conversation_context or any embedded questions
    print("\n[3] Checking session document for embedded questions...")
    if "conversation_context" in session_doc:
        print(f"  conversation_context: {session_doc['conversation_context']}")
    
    # Try to find the questions by their IDs in ANY collection
    print("\n[4] Listing ALL collections to find questions...")
    collections = await db.list_collection_names()
    for coll_name in collections:
        if 'question' in coll_name.lower():
            print(f"  Collection: {coll_name}")
            count = await db[coll_name].count_documents({})
            print(f"    Documents: {count}")
    
    client.close()

asyncio.run(find_questions())
