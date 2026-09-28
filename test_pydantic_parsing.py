#!/usr/bin/env python3
"""
Test if Pydantic correctly parses responses from MongoDB.
"""

import sys
sys.path.insert(0, "backend")

from app.database.models.interview_session import InterviewResponse

# Simulate MongoDB response data (what we saw from MongoDB)
mongo_response = {
    '_id': '6aba5acd588cf3b0d1ec749b',
    'created_at': '2026-09-28 12:17:17.362000',
    'updated_at': '2026-09-28 12:17:17.362000',
    'response_id': 'resp_1',
    'question_id': '6aba57b040f2ab6542a76729',
    'answer': 'test answer',
    'submitted_at': '2026-09-28 12:17:17.362000',
    'sequence_number': 1,
    'response_type': 'answer',
    'is_follow_up_to': None,
    'follow_up_question': None,
    'processing_duration_ms': None
    # NOTE: No 'evaluation' field - just like MongoDB
}

print("MongoDB response data:")
print(f"  Has 'evaluation' key: {'evaluation' in mongo_response}")
print()

try:
    # Try to parse with Pydantic
    response_obj = InterviewResponse(**mongo_response)
    
    print("Pydantic parsed successfully:")
    print(f"  response_id: {response_obj.response_id}")
    print(f"  evaluation: {response_obj.evaluation}")
    print(f"  evaluation is None: {response_obj.evaluation is None}")
    
except Exception as e:
    print(f"Pydantic parsing failed: {str(e)}")
    import traceback
    traceback.print_exc()
