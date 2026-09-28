"""
Interviewer Agent - Conducts conversational interviews with candidates.

This agent is responsible for:
1. Selecting the next question from the interview plan
2. Presenting questions naturally
3. Understanding candidate answers at a conversational level
4. Generating contextual follow-up questions when needed
5. Maintaining interview context and flow
6. Respecting interview plan and time constraints
7. Ending interviews appropriately

The agent does NOT evaluate or score candidates - that's handled separately.
"""

import logging
import json
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
from enum import Enum

from app.llm.service import llm_service, LLMException
from app.database.models.interview_session import (
    InterviewSession,
    InterviewStatus,
    ResponseType,
    InterviewResponse
)
from app.database.models.interview_plan import InterviewPlan, GeneratedQuestion
from app.database.models.resume_intelligence import CandidateProfile

logger = logging.getLogger(__name__)


class InterviewerAction(str, Enum):
    """Actions the interviewer can take."""
    ASK_QUESTION = "ask_question"
    ASK_FOLLOW_UP = "ask_follow_up"
    END_INTERVIEW = "end_interview"
    REQUEST_CLARIFICATION = "request_clarification"


class InterviewerException(Exception):
    """Exception for interviewer agent errors."""
    pass


class InterviewerDecision:
    """Structured decision from the interviewer agent."""
    
    def __init__(
        self,
        action: InterviewerAction,
        question: Optional[str] = None,
        question_id: Optional[str] = None,
        question_type: Optional[str] = None,
        skill: Optional[str] = None,
        reason: Optional[str] = None,
        is_follow_up: bool = False,
        source_question_id: Optional[str] = None,
        estimated_duration_seconds: int = 120,
        context_note: Optional[str] = None
    ):
        self.action = action
        self.question = question
        self.question_id = question_id
        self.question_type = question_type
        self.skill = skill
        self.reason = reason
        self.is_follow_up = is_follow_up
        self.source_question_id = source_question_id
        self.estimated_duration_seconds = estimated_duration_seconds
        self.context_note = context_note


class InterviewerAgent:
    """AI agent that conducts conversational interviews."""
    
    # Configuration constants
    MAX_FOLLOW_UPS_PER_QUESTION = 1
    MIN_ANSWER_LENGTH_FOR_FOLLOW_UP = 20  # characters
    MAX_CONTEXT_EXCHANGES = 3
    
    def __init__(self):
        """Initialize the interviewer agent."""
        self.logger = logger
    
    async def decide_next_action(
        self,
        session: InterviewSession,
        interview_plan: InterviewPlan,
        candidate_profile: CandidateProfile,
        last_answer: Optional[str] = None,
        last_question_id: Optional[str] = None
    ) -> InterviewerDecision:
        """
        Decide what to do next in the interview.
        
        Args:
            session: Current interview session
            interview_plan: Generated interview plan with questions
            candidate_profile: Candidate's profile
            last_answer: Last answer provided by candidate
            last_question_id: ID of the last question asked
            
        Returns:
            InterviewerDecision with next action to take
        """
        try:
            self.logger.info(f"Deciding next action for session {session.id}")
            
            # Check if interview should end
            if self._should_end_interview(session, interview_plan):
                return InterviewerDecision(
                    action=InterviewerAction.END_INTERVIEW,
                    reason="Interview plan completed or time limit reached"
                )
            
            # If we have a last answer, consider follow-up
            if last_answer and last_question_id:
                follow_up_decision = await self._consider_follow_up(
                    session,
                    interview_plan,
                    candidate_profile,
                    last_answer,
                    last_question_id
                )
                
                if follow_up_decision:
                    return follow_up_decision
            
            # Select next planned question
            next_question = self._select_next_question(session, interview_plan)
            if next_question:
                return InterviewerDecision(
                    action=InterviewerAction.ASK_QUESTION,
                    question=next_question.question,
                    question_id=next_question.question_id,
                    question_type=next_question.question_type.value,
                    skill=next_question.skill,
                    reason=f"Next question from interview plan: {next_question.reason}",
                    is_follow_up=False,
                    estimated_duration_seconds=next_question.estimated_duration_seconds
                )
            
            # No more questions available
            return InterviewerDecision(
                action=InterviewerAction.END_INTERVIEW,
                reason="No more questions available in interview plan"
            )
            
        except Exception as e:
            self.logger.error(f"Error in decide_next_action: {str(e)}")
            raise InterviewerException(f"Failed to decide next action: {str(e)}")
    
    async def _consider_follow_up(
        self,
        session: InterviewSession,
        interview_plan: InterviewPlan,
        candidate_profile: CandidateProfile,
        last_answer: str,
        last_question_id: str
    ) -> Optional[InterviewerDecision]:
        """
        Consider whether to ask a follow-up question based on the last answer.
        
        Args:
            session: Current session
            interview_plan: Interview plan
            candidate_profile: Candidate profile
            last_answer: Candidate's last answer
            last_question_id: ID of question being answered
            
        Returns:
            InterviewerDecision for follow-up or None if no follow-up needed
        """
        try:
            # Check if follow-up is allowed
            if not session.can_ask_follow_up(last_question_id, self.MAX_FOLLOW_UPS_PER_QUESTION):
                self.logger.info(f"Max follow-ups reached for question {last_question_id}")
                return None
            
            # Find the original question
            original_question = None
            for q in interview_plan.questions:
                if q.question_id == last_question_id:
                    original_question = q
                    break
            
            if not original_question:
                self.logger.warning(f"Original question {last_question_id} not found")
                return None
            
            # Check if follow-up is possible for this question
            if not original_question.follow_up_possible:
                return None
            
            # Use LLM to determine if follow-up is needed and generate it
            follow_up_question = await self._generate_follow_up_question(
                session,
                candidate_profile,
                original_question,
                last_answer
            )
            
            if follow_up_question:
                follow_up_id = f"{last_question_id}_follow_up_{len(session.get_follow_ups_for_question(last_question_id)) + 1}"
                
                return InterviewerDecision(
                    action=InterviewerAction.ASK_FOLLOW_UP,
                    question=follow_up_question,
                    question_id=follow_up_id,
                    question_type=original_question.question_type.value,
                    skill=original_question.skill,
                    reason="Follow-up based on candidate's answer",
                    is_follow_up=True,
                    source_question_id=last_question_id,
                    estimated_duration_seconds=90  # Follow-ups are typically shorter
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error considering follow-up: {str(e)}")
            return None
    
    async def _generate_follow_up_question(
        self,
        session: InterviewSession,
        candidate_profile: CandidateProfile,
        original_question: GeneratedQuestion,
        candidate_answer: str
    ) -> Optional[str]:
        """
        Generate a contextual follow-up question using LLM.
        
        Args:
            session: Current session
            candidate_profile: Candidate profile
            original_question: The question being followed up on
            candidate_answer: Candidate's answer to original question
            
        Returns:
            Follow-up question text or None if no follow-up needed
        """
        try:
            # Create context for LLM
            context = self._build_interview_context(session, candidate_profile)
            
            # Create follow-up generation prompt
            prompt = self._create_follow_up_prompt(
                context,
                original_question,
                candidate_answer
            )
            
            # Call LLM
            response = await llm_service.generate_structured_response(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "needs_follow_up": {
                            "type": "boolean",
                            "description": "Whether a follow-up question is needed"
                        },
                        "follow_up_question": {
                            "type": "string",
                            "description": "The follow-up question to ask"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Why this follow-up is being asked"
                        }
                    },
                    "required": ["needs_follow_up"]
                },
                temperature=0.7
            )
            
            if response and response.get("needs_follow_up"):
                follow_up = response.get("follow_up_question")
                if follow_up and len(follow_up.strip()) > 10:
                    self.logger.info(f"Generated follow-up: {follow_up}")
                    return follow_up.strip()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating follow-up question: {str(e)}")
            return None
    
    def _create_follow_up_prompt(
        self,
        context: Dict[str, Any],
        original_question: GeneratedQuestion,
        candidate_answer: str
    ) -> str:
        """Create prompt for follow-up question generation."""
        
        return f"""You are an expert technical interviewer conducting a {context['interview_type']} interview for a {context['target_position']} role.

CANDIDATE CONTEXT:
- Name: {context['candidate_name']}
- Key Skills: {', '.join(context['candidate_skills'][:5])}
- Target Role: {context['target_position']}

ORIGINAL QUESTION:
"{original_question.question}"

CANDIDATE'S ANSWER:
"{candidate_answer}"

QUESTION CONTEXT:
- Skill being tested: {original_question.skill}
- Question type: {original_question.question_type.value}
- Reason for asking: {original_question.reason}
- Expected topics: {', '.join(original_question.expected_topics)}

INTERVIEW GUIDELINES:
- Be professional and conversational
- Ask follow-ups when the answer is too brief, unclear, or mentions interesting technical details
- Don't repeat the same question
- Keep follow-ups focused and specific
- Don't give away the answer or provide hints

Based on the candidate's answer, determine if a follow-up question is needed and generate it if appropriate.

Consider asking a follow-up if:
1. The answer is too brief or lacks technical depth
2. The candidate mentioned a specific technology or approach worth exploring
3. There's an ambiguity that needs clarification
4. The candidate made a claim that should be substantiated

Respond with JSON containing:
- needs_follow_up: boolean
- follow_up_question: string (only if needs_follow_up is true)
- reason: string explaining the decision"""
    
    def _select_next_question(
        self,
        session: InterviewSession,
        interview_plan: InterviewPlan
    ) -> Optional[GeneratedQuestion]:
        """
        Select the next question from the interview plan.
        
        Args:
            session: Current session
            interview_plan: Interview plan with questions
            
        Returns:
            Next question to ask or None if no more questions
        """
        try:
            # Find questions that haven't been asked yet
            available_questions = [
                q for q in interview_plan.questions
                if not session.is_question_asked(q.question_id)
            ]
            
            if not available_questions:
                return None
            
            # For now, follow the order in the interview plan
            # In the future, this could implement adaptive selection based on answers
            return available_questions[0]
            
        except Exception as e:
            self.logger.error(f"Error selecting next question: {str(e)}")
            return None
    
    def _should_end_interview(
        self,
        session: InterviewSession,
        interview_plan: InterviewPlan
    ) -> bool:
        """
        Determine if the interview should end.
        
        Args:
            session: Current session
            interview_plan: Interview plan
            
        Returns:
            True if interview should end
        """
        try:
            # Check if all questions have been asked
            total_questions = len(interview_plan.questions)
            asked_questions = len(session.completed_question_ids)
            
            if asked_questions >= total_questions:
                self.logger.info("All planned questions have been asked")
                return True
            
            # Check time limit (if interview has started)
            if session.actual_start_time:
                elapsed_time = datetime.utcnow() - session.actual_start_time
                # Add pause time
                total_elapsed = elapsed_time.total_seconds() + session.pause_duration_seconds
                max_time_seconds = session.duration_minutes * 60
                
                if total_elapsed >= max_time_seconds:
                    self.logger.info("Interview time limit reached")
                    return True
            
            # Check if we've reached the target question count
            if session.current_question_index >= session.question_count:
                self.logger.info("Target question count reached")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if interview should end: {str(e)}")
            return False
    
    def _build_interview_context(
        self,
        session: InterviewSession,
        candidate_profile: CandidateProfile
    ) -> Dict[str, Any]:
        """
        Build compact context object for LLM.
        
        Args:
            session: Current session
            candidate_profile: Candidate profile
            
        Returns:
            Compact context dictionary
        """
        try:
            # Get recent conversation context
            recent_context = session.get_recent_context(self.MAX_CONTEXT_EXCHANGES)
            
            context = {
                "candidate_name": candidate_profile.candidate_name or "Candidate",
                "target_position": session.target_position,
                "target_company": session.target_company,
                "interview_type": session.interview_type.value,
                "difficulty": session.difficulty_level.value,
                "candidate_skills": [],
                "relevant_projects": [],
                "recent_conversation": recent_context,
                "questions_asked": len(session.completed_question_ids),
                "total_questions_planned": session.question_count,
                "interview_duration_minutes": session.duration_minutes
            }
            
            # Add candidate skills
            if candidate_profile.skills:
                if candidate_profile.skills.programming_languages:
                    context["candidate_skills"].extend(candidate_profile.skills.programming_languages)
                if candidate_profile.skills.frameworks:
                    context["candidate_skills"].extend(candidate_profile.skills.frameworks)
                if candidate_profile.skills.databases:
                    context["candidate_skills"].extend(candidate_profile.skills.databases)
            
            # Add relevant projects (top 3)
            if candidate_profile.projects:
                for project in candidate_profile.projects[:3]:
                    if hasattr(project, 'name') and hasattr(project, 'technologies'):
                        context["relevant_projects"].append({
                            "name": project.name,
                            "technologies": project.technologies[:5]  # Top 5 technologies
                        })
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error building interview context: {str(e)}")
            return {
                "candidate_name": "Candidate",
                "target_position": session.target_position,
                "interview_type": session.interview_type.value,
                "difficulty": session.difficulty_level.value,
                "candidate_skills": [],
                "relevant_projects": [],
                "recent_conversation": [],
                "questions_asked": 0,
                "total_questions_planned": session.question_count
            }
    
    def create_interviewer_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create the system prompt for the interviewer agent.
        
        Args:
            context: Interview context
            
        Returns:
            System prompt for the interviewer
        """
        return f"""You are an expert technical interviewer conducting a {context['interview_type']} interview for a {context['target_position']} position at {context.get('target_company', 'the company')}.

INTERVIEWER GUIDELINES:
1. Be professional, conversational, and encouraging
2. Ask one question at a time
3. Stay relevant to the target role and candidate's background
4. Use the candidate's resume information when appropriate
5. Ask natural follow-up questions when needed
6. Avoid giving away answers or providing hints
7. Don't evaluate or score the candidate explicitly
8. Avoid unnecessary praise or criticism
9. Maintain good conversational flow
10. Never invent or assume candidate experience not in their resume

CANDIDATE CONTEXT:
- Name: {context['candidate_name']}
- Target Role: {context['target_position']}
- Key Skills: {', '.join(context['candidate_skills'][:8]) if context['candidate_skills'] else 'Not specified'}
- Interview Type: {context['interview_type']}
- Difficulty Level: {context['difficulty']}

RELEVANT PROJECTS:
{chr(10).join([f"- {p['name']}: {', '.join(p['technologies'])}" for p in context['relevant_projects']]) if context['relevant_projects'] else 'None listed'}

INTERVIEW PROGRESS:
- Questions asked so far: {context['questions_asked']}
- Total questions planned: {context['total_questions_planned']}
- Duration: {context.get('interview_duration_minutes', 60)} minutes

RECENT CONVERSATION:
{chr(10).join([f"Q{c['sequence']}: {c.get('question', 'N/A')} -> A: {c['answer'][:100]}..." for c in context['recent_conversation']]) if context['recent_conversation'] else 'No previous exchanges'}

Remember: Your role is to conduct the interview professionally and gather information about the candidate's abilities. Leave evaluation and scoring to other systems."""


# Global instance
interviewer_agent = InterviewerAgent()

__all__ = [
    'InterviewerAgent',
    'InterviewerAction',
    'InterviewerDecision',
    'InterviewerException',
    'interviewer_agent',
]