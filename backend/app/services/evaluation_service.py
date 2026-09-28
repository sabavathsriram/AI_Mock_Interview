"""
Evaluation Service for processing interview answers and generating evaluations.
"""

import json
import logging
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import ValidationError

from app.database.mongodb import mongodb
from app.database.models.candidate_answer import CandidateAnswer
from app.database.models.evaluation import Evaluation, EvaluationCategory
from app.database.models.interview_question import InterviewQuestion
from app.llm.service import llm_service
from app.llm.prompts import PromptType

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating interview answers and generating evaluation reports."""

    async def evaluate_interview_answers(
        self,
        interview_session_id: str,
        user_id: str,
        target_position: str,
        difficulty_level: str,
    ) -> Optional[Evaluation]:
        """
        Evaluate all answers for a completed interview session.

        This method:
        1. Fetches all answers for the session
        2. Evaluates each answer using LLM
        3. Aggregates scores by category
        4. Generates overall evaluation with strengths/weaknesses
        5. Stores Evaluation document in MongoDB

        Args:
            interview_session_id: ID of the completed interview session
            user_id: ID of the user
            target_position: Position the interview was for
            difficulty_level: Difficulty level of the interview

        Returns:
            Evaluation document if successful, None if evaluation fails
        """
        try:
            # Fetch all answers for this session
            answers_collection = mongodb.get_collection("candidate_answers")
            answers = await answers_collection.find({
                "interview_session_id": interview_session_id,
                "user_id": user_id,
                "is_submitted": True
            }).to_list(None)

            if not answers:
                logger.warning(f"No submitted answers found for session {interview_session_id}")
                return None

            logger.info(f"Evaluating {len(answers)} answers for session {interview_session_id}")

            # Evaluate each answer and collect feedback
            category_scores: Dict[str, List[float]] = {}
            all_strengths: List[str] = []
            all_weaknesses: List[str] = []
            all_feedback: List[str] = []
            total_score = 0

            for idx, answer in enumerate(answers):
                try:
                    # Get the question for context
                    questions_collection = mongodb.get_collection("interview_questions")
                    question = await questions_collection.find_one({
                        "_id": answer.get("question_id")
                    })

                    if not question:
                        logger.warning(f"Question not found for answer {answer.get('_id')}")
                        continue

                    # Evaluate this answer
                    answer_eval = await self._evaluate_single_answer(
                        question=question,
                        answer=answer,
                        position_level=difficulty_level
                    )

                    if answer_eval:
                        # Extract scores from evaluation
                        score = answer_eval.get("score", 5)  # Default to 5 if not present
                        score_0_100 = (score / 10) * 100  # Convert 1-10 to 0-100

                        # Store in answer document
                        await answers_collection.update_one(
                            {"_id": answer.get("_id")},
                            {
                                "$set": {
                                    "ai_score": score_0_100,
                                    "ai_feedback": answer_eval.get("feedback", ""),
                                    "confidence_score": answer_eval.get("confidence", 0.7),
                                    "clarity_score": answer_eval.get("clarity", score / 10),
                                    "completeness_score": answer_eval.get("completeness", score / 10),
                                    "evaluated_at": datetime.utcnow()
                                }
                            }
                        )

                        # Categorize the answer
                        category = question.get("category", "General")
                        if category not in category_scores:
                            category_scores[category] = []
                        category_scores[category].append(score_0_100)

                        # Collect strengths and weaknesses
                        if answer_eval.get("strengths"):
                            all_strengths.extend(answer_eval["strengths"])
                        if answer_eval.get("improvements"):
                            all_weaknesses.extend(answer_eval["improvements"])

                        all_feedback.append(answer_eval.get("feedback", ""))
                        total_score += score_0_100

                except Exception as e:
                    logger.error(f"Error evaluating answer {answer.get('_id')}: {str(e)}")
                    continue

            if not category_scores:
                logger.warning("No answers were successfully evaluated")
                return None

            # Calculate category averages
            category_list: List[EvaluationCategory] = []
            category_scores_dict: Dict[str, float] = {}

            for category, scores in category_scores.items():
                avg_score = sum(scores) / len(scores)
                category_scores_dict[category] = avg_score
                category_list.append(
                    EvaluationCategory(
                        name=category,
                        weight=1.0 / len(category_scores),
                        score=avg_score,
                        feedback=f"Average score for {category}: {avg_score:.1f}%"
                    )
                )

            # Calculate overall score
            overall_score = total_score / len(answers)

            # Calculate composite scores
            technical_score = category_scores_dict.get("System Design", 0) or \
                             category_scores_dict.get("Technical Knowledge", overall_score)
            communication_score = category_scores_dict.get("Communication", overall_score)
            problem_solving_score = category_scores_dict.get("Problem Solving", overall_score)

            # Create evaluation document
            evaluation = Evaluation(
                interview_session_id=interview_session_id,
                user_id=user_id,
                overall_score=overall_score,
                overall_feedback=self._generate_overall_feedback(
                    overall_score,
                    all_strengths,
                    all_weaknesses
                ),
                categories=category_list,
                strengths=list(set(all_strengths[:5])),  # Top 5 unique strengths
                weaknesses=list(set(all_weaknesses[:5])),  # Top 5 unique weaknesses
                improvement_areas=[f"Improve {w.lower()}" for w in all_weaknesses[:3]],
                technical_knowledge_score=technical_score,
                communication_score=communication_score,
                problem_solving_score=problem_solving_score,
                skill_gaps=list(set(all_weaknesses[:3])),
                training_recommendations=[f"Focus on: {w}" for w in all_weaknesses[:3]],
                is_ai_generated=True,
                ai_model_used="gemini",
                confidence_score=0.85,
            )

            # Store evaluation in MongoDB
            evaluations_collection = mongodb.get_collection("evaluations")
            result = await evaluations_collection.insert_one(evaluation.dict(by_alias=True))
            evaluation_id = str(result.inserted_id)

            # Update interview session with overall score
            interviews_collection = mongodb.get_collection("interviews")
            from bson import ObjectId
            await interviews_collection.update_one(
                {"_id": ObjectId(interview_session_id)},
                {
                    "$set": {
                        "overall_score": overall_score,
                        "evaluation_id": evaluation_id,
                        "evaluated_at": datetime.utcnow()
                    }
                }
            )

            logger.info(f"Evaluation complete for session {interview_session_id}. Score: {overall_score:.2f}")
            return evaluation

        except Exception as e:
            logger.error(f"Error generating evaluation: {str(e)}", exc_info=True)
            return None

    async def _evaluate_single_answer(
        self,
        question: Dict,
        answer: Dict,
        position_level: str
    ) -> Optional[Dict]:
        """
        Evaluate a single answer using LLM.

        Args:
            question: Question document
            answer: Answer document
            position_level: Level of the position (easy/medium/hard)

        Returns:
            Dictionary with score, feedback, strengths, improvements
        """
        try:
            # Prepare evaluation prompt
            answer_text = answer.get("answer_text", "")
            question_text = question.get("question_text", "")
            key_points = question.get("key_points", [])
            expected_areas = ", ".join(key_points) if key_points else "General understanding"

            prompt = f"""
Question: {question_text}

Candidate Answer: {answer_text}

Expected Knowledge Areas: {expected_areas}
Position Level: {position_level}

Please evaluate this answer on a scale of 1-10 and provide:
1. Score (1-10)
2. Strengths (2-3 bullet points)
3. Areas for improvement (2-3 bullet points)
4. Clarity score (1-10)
5. Completeness score (1-10)

Respond in JSON format with fields: score, feedback, strengths, improvements, clarity, completeness, confidence
"""

            # Call LLM for evaluation
            response = await llm_service.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=500,
                system_prompt="You are an expert interviewer evaluating candidate responses. Be fair and constructive."
            )

            # Parse response
            response_text = response.text.strip()

            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                evaluation = json.loads(json_str)
                return evaluation
            else:
                # Fallback: structured response but with simpler score
                logger.warning(f"Could not extract JSON from LLM response: {response_text[:100]}")
                return {
                    "score": 6,
                    "feedback": response_text[:200],
                    "strengths": ["Attempted answer"],
                    "improvements": ["Could be more detailed"],
                    "clarity": 0.6,
                    "completeness": 0.6,
                    "confidence": 0.5
                }

        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}")
            return None

    def _generate_overall_feedback(
        self,
        score: float,
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """Generate overall feedback based on score and identified areas."""
        if score >= 85:
            feedback = "Excellent performance! You demonstrated strong technical knowledge and clear communication."
        elif score >= 75:
            feedback = "Good performance. You showed solid understanding with room for improvement in some areas."
        elif score >= 65:
            feedback = "Satisfactory performance. Consider focusing on the improvement areas identified."
        else:
            feedback = "Your performance shows potential but needs focused improvement in several areas."

        if strengths:
            feedback += f" Key strengths: {', '.join(strengths[:2])}."

        return feedback

    async def get_evaluation(self, interview_session_id: str, user_id: str) -> Optional[Evaluation]:
        """
        Retrieve evaluation for an interview session.

        Args:
            interview_session_id: Interview session ID
            user_id: User ID

        Returns:
            Evaluation document or None if not found
        """
        try:
            evaluations_collection = mongodb.get_collection("evaluations")
            evaluation = await evaluations_collection.find_one({
                "interview_session_id": interview_session_id,
                "user_id": user_id
            })

            if evaluation:
                # Convert to Evaluation model
                return Evaluation(**evaluation)

            return None

        except Exception as e:
            logger.error(f"Error retrieving evaluation: {str(e)}")
            return None


# Global instance
evaluation_service = EvaluationService()
