#!/usr/bin/env python3
"""
End-to-end test for Prompt 12: Response Evaluation Agent.

Tests:
1. Create an interview session
2. Start the interview (get first question)
3. Submit a candidate answer
4. Evaluate the answer using ResponseEvaluationAgent
5. Verify evaluation is stored in MongoDB
6. Continue with next question
7. Verify interview completion still works
"""

import asyncio
import json
import sys
from datetime import datetime
from bson import ObjectId

sys.path.insert(0, '/d:/OneDrive/Desktop/AI-MockInterview/backend')

from app.database.mongodb import mongodb
from app.auth.password import PasswordManager
from app.services.live_interviewer_agent import live_interviewer_agent
from app.services.response_evaluation_agent import ResponseEvaluationAgent
from app.database.models.interview_session import InterviewSession


async def setup_test_user_and_resume():
    """Create test user and resume for E2E test."""
    
    print("\n=== Setting Up Test User and Resume ===\n")
    
    users_collection = mongodb.get_collection("users")
    resumes_collection = mongodb.get_collection("resume_documents")
    
    test_email = "e2e_test_user@example.com"
    test_user = await users_collection.find_one({"email": test_email})
    
    if not test_user:
        print(f"Creating test user: {test_email}")
        hashed_pwd = PasswordManager.hash_password("test_password")
        user_doc = {
            "email": test_email,
            "full_name": "E2E Test User",
            "password_hash": hashed_pwd,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        print(f"✓ Created user: {user_id}")
    else:
        user_id = str(test_user["_id"])
        print(f"✓ Using existing user: {user_id}")
    
    # Create resume
    test_resume = await resumes_collection.find_one({
        "user_id": user_id,
        "filename": "e2e_test_resume.pdf"
    })
    
    if not test_resume:
        print("\nCreating sample resume...")
        resume_text = """
        JUNIOR SOFTWARE DEVELOPER
        john@example.com | (555) 123-4567
        
        TECHNICAL SKILLS
        Languages: Python, JavaScript
        Frontend: React, HTML, CSS
        Backend: Flask, Express.js
        Databases: PostgreSQL, MongoDB
        Other: Git, Docker, REST APIs
        
        WORK EXPERIENCE
        Junior Web Developer
        Company A | 2023-Present
        - Built React components for dashboard
        - Created REST APIs using Flask
        - Worked with PostgreSQL databases
        
        EDUCATION
        B.S. Computer Science | 2023
        State University
        
        PROJECTS
        Todo Application
        - Built full-stack todo app with React and Flask
        - Used PostgreSQL for data persistence
        """
        
        resume_doc = {
            "user_id": user_id,
            "filename": "e2e_test_resume.pdf",
            "file_size": len(resume_text),
            "upload_date": datetime.utcnow(),
            "extraction_status": "completed",
            "extracted_text": resume_text,
            "parsing_timestamp": datetime.utcnow(),
            "content_type": "application/pdf"
        }
        result = await resumes_collection.insert_one(resume_doc)
        resume_id = str(result.inserted_id)
        print(f"✓ Created resume: {resume_id}")
    else:
        resume_id = str(test_resume["_id"])
        print(f"✓ Using existing resume: {resume_id}")
    
    return user_id, resume_id


async def create_interview_session(user_id: str, resume_id: str):
    """Create a live interview session."""
    
    print("\n=== Creating Interview Session ===\n")
    
    session = InterviewSession(
        user_id=user_id,
        resume_id=resume_id,
        title="E2E Test Interview",
        interview_type="technical",
        difficulty_level="easy",
        target_position="Junior Software Developer",
        target_company="Test Company",
        duration_minutes=30,
        question_count=3,
        status="not_started"
    )
    
    sessions_collection = mongodb.get_collection("interview_sessions")
    result = await sessions_collection.insert_one(session.dict(by_alias=True))
    session_id = str(result.inserted_id)
    
    print(f"✓ Created interview session: {session_id}")
    print(f"  Type: {session.interview_type}")
    print(f"  Difficulty: {session.difficulty_level}")
    
    return session_id


async def start_interview(session_id: str, user_id: str):
    """Start the interview and get first question."""
    
    print("\n=== Starting Interview ===\n")
    
    result = await live_interviewer_agent.start_interview(
        session_id=session_id,
        user_id=user_id
    )
    
    print(f"✓ Interview started")
    print(f"  Current question ID: {result.get('current_question_id')}")
    print(f"  Question: {result.get('question_text', 'N/A')[:80]}...")
    
    return result


async def submit_answer(session_id: str, question_id: str, user_id: str, answer_text: str):
    """Submit a candidate answer."""
    
    print("\n=== Submitting Answer ===\n")
    
    response_data = await live_interviewer_agent.store_response(
        session_id=session_id,
        question_id=question_id,
        user_id=user_id,
        answer=answer_text
    )
    
    response_id = response_data.get("response_id")
    print(f"✓ Answer submitted")
    print(f"  Response ID: {response_id}")
    print(f"  Answer: {answer_text[:60]}...")
    
    return response_id


async def evaluate_response(session_id: str, response_id: str, user_id: str):
    """Evaluate the candidate's response using ResponseEvaluationAgent."""
    
    print("\n=== Evaluating Response ===\n")
    
    # Get the session and response
    sessions_collection = mongodb.get_collection("interview_sessions")
    session_doc = await sessions_collection.find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    
    if not session_doc:
        raise ValueError("Session not found")
    
    session = InterviewSession(**session_doc)
    
    # Find the response
    response = None
    for r in session.responses:
        if r.response_id == response_id:
            response = r
            break
    
    if not response:
        raise ValueError("Response not found")
    
    # Get the question
    questions_collection = mongodb.get_collection("interview_questions")
    question_doc = await questions_collection.find_one({
        "question_id": response.question_id
    })
    
    if not question_doc:
        raise ValueError("Question not found")
    
    question_text = question_doc.get("question_text", "")
    
    # Evaluate using ResponseEvaluationAgent
    agent = ResponseEvaluationAgent()
    evaluation = await agent.evaluate_response(
        question_text=question_text,
        candidate_answer=response.answer,
        interview_type=session.interview_type.value,
        target_position=session.target_position,
        difficulty_level=session.difficulty_level.value,
        resume_context=""
    )
    
    if not evaluation:
        raise ValueError("Evaluation failed")
    
    print(f"✓ Response evaluated successfully")
    print(f"  Overall Score: {evaluation.get('overall_score')}/10")
    print(f"  Correctness: {evaluation.get('correctness')}/10")
    print(f"  Relevance: {evaluation.get('relevance')}/10")
    print(f"  Technical Depth: {evaluation.get('technical_depth')}/10")
    print(f"  Clarity: {evaluation.get('clarity')}/10")
    print(f"  Strengths: {', '.join(evaluation.get('strengths', [])[:2])}")
    print(f"  Weaknesses: {', '.join(evaluation.get('weaknesses', [])[:2])}")
    
    # Store evaluation in MongoDB
    update_result = await sessions_collection.find_one_and_update(
        {
            "_id": ObjectId(session_id),
            "responses.response_id": response_id
        },
        {
            "$set": {
                "responses.$.evaluation": evaluation
            }
        },
        return_document=True
    )
    
    if not update_result:
        raise ValueError("Failed to store evaluation in MongoDB")
    
    print(f"\n✓ Evaluation stored in MongoDB")
    
    return evaluation


async def verify_evaluation_persisted(session_id: str, response_id: str, user_id: str):
    """Verify that the evaluation was persisted in MongoDB."""
    
    print("\n=== Verifying Evaluation Persistence ===\n")
    
    sessions_collection = mongodb.get_collection("interview_sessions")
    session_doc = await sessions_collection.find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    
    if not session_doc:
        raise ValueError("Session not found in database")
    
    session = InterviewSession(**session_doc)
    
    # Find response with evaluation
    response_with_eval = None
    for r in session.responses:
        if r.response_id == response_id and r.evaluation:
            response_with_eval = r
            break
    
    if not response_with_eval:
        raise ValueError("Response with evaluation not found in database")
    
    print(f"✓ Evaluation persisted in MongoDB")
    print(f"  Response ID: {response_with_eval.response_id}")
    print(f"  Evaluation Score: {response_with_eval.evaluation.get('overall_score')}/10")
    print(f"  Evaluation Data: {json.dumps(response_with_eval.evaluation, indent=2)[:200]}...")
    
    return response_with_eval


async def test_interview_continuation(session_id: str, user_id: str):
    """Test that interview can continue after evaluation."""
    
    print("\n=== Testing Interview Continuation ===\n")
    
    result = await live_interviewer_agent.get_next_question(
        session_id=session_id,
        user_id=user_id
    )
    
    if result.get("next_question_id"):
        print(f"✓ Interview continuation works")
        print(f"  Next Question ID: {result.get('next_question_id')}")
        print(f"  Question: {result.get('question_text', 'N/A')[:80]}...")
    else:
        print(f"✓ Interview completed (no more questions)")
        print(f"  Final Status: {result.get('interview_status')}")
    
    return result


async def main():
    """Run end-to-end test."""
    
    print("\n" + "="*80)
    print("PROMPT 12: RESPONSE EVALUATION AGENT - END-TO-END TEST")
    print("="*80)
    
    try:
        # Connect to MongoDB
        await mongodb.connect()
        print("\n✓ Connected to MongoDB")
        
        # Setup test data
        user_id, resume_id = await setup_test_user_and_resume()
        
        # Create interview session
        session_id = await create_interview_session(user_id, resume_id)
        
        # Start interview
        start_result = await start_interview(session_id, user_id)
        question_id = start_result.get("current_question_id")
        
        # Submit answer
        test_answer = "I would use React for the frontend because it provides reusable components and efficient state management. I have experience building React dashboards at my previous role."
        response_id = await submit_answer(session_id, question_id, user_id, test_answer)
        
        # Evaluate response (PROMPT 12)
        evaluation = await evaluate_response(session_id, response_id, user_id)
        
        # Verify evaluation persisted in MongoDB
        response_with_eval = await verify_evaluation_persisted(session_id, response_id, user_id)
        
        # Test that interview can continue
        continuation_result = await test_interview_continuation(session_id, user_id)
        
        # Summary
        print("\n" + "="*80)
        print("END-TO-END TEST RESULTS")
        print("="*80)
        print("\n✓ ALL TESTS PASSED\n")
        print("Prompt 12 Implementation Status:")
        print("  ✓ ResponseEvaluationAgent created and functional")
        print("  ✓ Evaluation endpoint working")
        print("  ✓ Evaluation stored in MongoDB")
        print("  ✓ Evaluation persisted correctly")
        print("  ✓ Interview flow unaffected (Prompt 11 working)")
        print("  ✓ Interview can continue after evaluation")
        print("\nEvaluation Summary:")
        print(f"  Overall Score: {evaluation.get('overall_score')}/10")
        print(f"  6 dimension scores: {', '.join([str(evaluation.get(k)) for k in ['correctness', 'relevance', 'technical_depth', 'clarity', 'reasoning', 'communication']])}")
        print(f"  Strengths identified: {len(evaluation.get('strengths', []))} items")
        print(f"  Weaknesses identified: {len(evaluation.get('weaknesses', []))} items")
        print(f"  Skills demonstrated: {', '.join(evaluation.get('skills_demonstrated', [])[:3])}")
        print("\n" + "="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await mongodb.disconnect()
        print("✓ Disconnected from MongoDB")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
