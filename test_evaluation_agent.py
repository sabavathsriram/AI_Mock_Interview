#!/usr/bin/env python3
"""
Test ResponseEvaluationAgent directly with Groq.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, "backend")

# Load environment variables
from dotenv import load_dotenv
load_dotenv("backend/.env")

from app.services.response_evaluation_agent import ResponseEvaluationAgent
from app.llm.config import llm_settings

async def main():
    print("=" * 60)
    print("Testing ResponseEvaluationAgent")
    print("=" * 60)
    
    # Check LLM configuration
    print(f"\n=== LLM CONFIGURATION ===")
    print(f"LLM Configured: {llm_settings.is_configured()}")
    print(f"API Key set: {bool(llm_settings.groq_api_key)}")
    print(f"Model: {llm_settings.groq_model}")
    
    if not llm_settings.is_configured():
        print("\nERROR: LLM is NOT configured!")
        return
    
    # Create agent
    agent = ResponseEvaluationAgent()
    print(f"Agent model: {agent.model_used}")
    print(f"LLM service configured: {agent.llm_service.configured}")
    
    # Test question and answer
    question = "Explain event handling in JavaScript. How would you implement a click handler on a button element?"
    answer = "i have created a fullstack project using javascript , i have implemented event handling like onmouse and and other and used asysnchronous to fetch data and used dom to manipulate the things"
    
    print(f"\n=== TEST EVALUATION ===")
    print(f"Question: {question[:60]}...")
    print(f"Answer: {answer[:60]}...")
    
    try:
        print(f"\nCalling ResponseEvaluationAgent.evaluate_response()...")
        evaluation = await agent.evaluate_response(
            question_text=question,
            candidate_answer=answer,
            interview_type="technical",
            target_position="Software Engineer",
            difficulty_level="medium",
            resume_context=""
        )
        
        if evaluation is None:
            print(f"ERROR: Agent returned None!")
            return
        
        print(f"\n[SUCCESS] Evaluation successful!")
        print(f"Overall Score: {evaluation.get('overall_score')}/10")
        print(f"Correctness: {evaluation.get('correctness')}/10")
        print(f"Relevance: {evaluation.get('relevance')}/10")
        print(f"Technical Depth: {evaluation.get('technical_depth')}/10")
        print(f"Clarity: {evaluation.get('clarity')}/10")
        print(f"Strengths: {evaluation.get('strengths', [])[:2]}")
        print(f"Weaknesses: {evaluation.get('weaknesses', [])[:2]}")
        
    except Exception as e:
        print(f"ERROR: Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
