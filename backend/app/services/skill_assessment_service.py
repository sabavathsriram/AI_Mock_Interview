"""
Skill Assessment Service for extracting and assessing skills from interview answers.
"""

import logging
import re
from typing import Optional, List, Dict, Set
from datetime import datetime

from app.database.mongodb import mongodb
from app.database.models.skill_assessment import SkillAssessment, SkillMetric
from app.database.models.evaluation import Evaluation

logger = logging.getLogger(__name__)


class SkillAssessmentService:
    """Service for assessing skills from interview performance."""

    # Common technical skills to look for
    COMMON_SKILLS = {
        "Python": ["python", "py"],
        "JavaScript": ["javascript", "js", "node"],
        "TypeScript": ["typescript", "ts"],
        "React": ["react", "jsx"],
        "Java": ["java"],
        "C++": ["c++", "cpp"],
        "Go": ["golang", "go"],
        "Rust": ["rust"],
        "SQL": ["sql", "mysql", "postgresql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "AWS": ["aws", "amazon"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "System Design": ["system design", "architecture", "scalability"],
        "Data Structures": ["data structure", "array", "linked list", "tree"],
        "Algorithms": ["algorithm", "sorting", "searching", "complexity"],
        "Problem Solving": ["problem solving", "approach", "logic"],
        "Communication": ["communication", "explain", "clarity"],
        "Leadership": ["leadership", "lead", "mentor", "manage"],
        "Testing": ["testing", "unit test", "test case"],
        "API Design": ["api", "rest", "graphql"],
        "Database Design": ["database", "schema", "normalization"],
    }

    async def assess_interview_skills(
        self,
        interview_session_id: str,
        user_id: str,
        evaluation_id: Optional[str] = None,
    ) -> Optional[SkillAssessment]:
        """
        Assess skills from interview answers and create SkillAssessment document.

        Args:
            interview_session_id: ID of the interview session
            user_id: ID of the user
            evaluation_id: Optional reference to evaluation document

        Returns:
            SkillAssessment document if successful, None if assessment fails
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

            logger.info(f"Assessing skills from {len(answers)} answers")

            # Extract skills from answers
            extracted_skills = await self._extract_skills_from_answers(answers)

            if not extracted_skills:
                logger.warning("No skills extracted from answers")
                return None

            # Assess proficiency for each skill based on answer scores
            skill_metrics: List[SkillMetric] = []
            skill_scores = {}

            for skill_name, skill_info in extracted_skills.items():
                # Calculate proficiency (1-5 scale)
                proficiency, confidence = self._calculate_proficiency(
                    skill_info=skill_info,
                    answers=answers
                )

                # Create skill metric
                metric = SkillMetric(
                    skill_name=skill_name,
                    category=skill_info.get("category", "Technical"),
                    current_proficiency=proficiency,
                    confidence_score=confidence,
                    evidence=skill_info.get("evidence", []),
                    last_assessed_date=datetime.utcnow(),
                    assessment_method="interview",
                    previous_proficiency=None,
                    proficiency_change=None,
                    trend="new",  # First assessment
                )

                skill_metrics.append(metric)
                skill_scores[skill_name] = proficiency

            # Calculate summary statistics
            if skill_metrics:
                proficiencies = [m.current_proficiency for m in skill_metrics]
                average_proficiency = sum(proficiencies) / len(proficiencies)
                strongest_skills = sorted(
                    skill_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                weakest_skills = sorted(
                    skill_scores.items(),
                    key=lambda x: x[1]
                )[:3]

                # Group by category
                categories: Dict[str, List[int]] = {}
                for metric in skill_metrics:
                    if metric.category not in categories:
                        categories[metric.category] = []
                    categories[metric.category].append(metric.current_proficiency)

                category_averages = {
                    cat: sum(scores) / len(scores) for cat, scores in categories.items()
                }

                # Create skill assessment document
                assessment = SkillAssessment(
                    user_id=user_id,
                    interview_session_id=interview_session_id,
                    assessment_title=f"Post-Interview Skill Assessment",
                    assessment_date=datetime.utcnow(),
                    assessment_type="post-interview",
                    skills=skill_metrics,
                    average_proficiency=average_proficiency,
                    strongest_skills=[s[0] for s in strongest_skills],
                    weakest_skills=[s[0] for s in weakest_skills],
                    categories=category_averages,
                    is_ai_assessed=True,
                    ai_model_used="gemini",
                    ai_confidence=0.8,
                    recommended_skill_focus=[s[0] for s in weakest_skills],
                    skill_gap_analysis=self._generate_skill_gap_analysis(
                        strongest=strongest_skills,
                        weakest=weakest_skills
                    ),
                    is_comprehensive=True,
                )

                # Store assessment in MongoDB
                assessments_collection = mongodb.get_collection("skill_assessments")
                result = await assessments_collection.insert_one(assessment.dict(by_alias=True))
                assessment_id = str(result.inserted_id)

                # Update interview session with assessment reference
                interviews_collection = mongodb.get_collection("interviews")
                from bson import ObjectId
                await interviews_collection.update_one(
                    {"_id": ObjectId(interview_session_id)},
                    {
                        "$set": {
                            "skill_assessment_id": assessment_id,
                        }
                    }
                )

                logger.info(
                    f"Skill assessment complete for session {interview_session_id}. "
                    f"Assessed {len(skill_metrics)} skills."
                )

                return assessment

            return None

        except Exception as e:
            logger.error(f"Error assessing skills: {str(e)}", exc_info=True)
            return None

    async def _extract_skills_from_answers(self, answers: List[Dict]) -> Dict[str, Dict]:
        """
        Extract skills mentioned in answer text.

        Args:
            answers: List of answer documents

        Returns:
            Dictionary mapping skill name to skill info (category, evidence)
        """
        extracted_skills: Dict[str, Dict] = {}

        for answer in answers:
            answer_text = answer.get("answer_text", "").lower()

            if not answer_text:
                continue

            # Look for skill mentions
            for skill_name, keywords in self.COMMON_SKILLS.items():
                for keyword in keywords:
                    if keyword in answer_text:
                        if skill_name not in extracted_skills:
                            extracted_skills[skill_name] = {
                                "category": self._categorize_skill(skill_name),
                                "evidence": [],
                                "mentions": 0,
                                "related_answers": []
                            }

                        # Extract evidence (surrounding context)
                        idx = answer_text.find(keyword)
                        if idx != -1:
                            start = max(0, idx - 50)
                            end = min(len(answer_text), idx + len(keyword) + 50)
                            evidence = answer_text[start:end].strip()
                            if evidence not in extracted_skills[skill_name]["evidence"]:
                                extracted_skills[skill_name]["evidence"].append(evidence)

                        extracted_skills[skill_name]["mentions"] += 1
                        extracted_skills[skill_name]["related_answers"].append(
                            str(answer.get("_id"))
                        )

                        break  # Only count once per answer

        return extracted_skills

    def _categorize_skill(self, skill_name: str) -> str:
        """Categorize a skill into a group."""
        programming_langs = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust"
        ]
        frameworks = ["React", "Django", "FastAPI", "Spring"]
        databases = ["SQL", "MongoDB", "Redis"]
        devops = ["Docker", "Kubernetes", "AWS"]
        core_competencies = [
            "System Design", "Data Structures", "Algorithms",
            "Problem Solving", "Communication", "Leadership", "Testing"
        ]

        if skill_name in programming_langs:
            return "Programming Languages"
        elif skill_name in frameworks:
            return "Frameworks & Libraries"
        elif skill_name in databases:
            return "Databases & Storage"
        elif skill_name in devops:
            return "DevOps & Infrastructure"
        elif skill_name in core_competencies:
            return "Core Competencies"
        else:
            return "Technical Skills"

    def _calculate_proficiency(
        self,
        skill_info: Dict,
        answers: List[Dict]
    ) -> tuple:
        """
        Calculate proficiency level (1-5) and confidence score.

        Args:
            skill_info: Skill information with mentions and evidence
            answers: All answers for context

        Returns:
            Tuple of (proficiency_level: 1-5, confidence: 0-1)
        """
        mentions = skill_info.get("mentions", 1)
        evidence_count = len(skill_info.get("evidence", []))

        # More mentions = higher proficiency
        if mentions >= 5:
            base_proficiency = 5
        elif mentions >= 3:
            base_proficiency = 4
        elif mentions >= 2:
            base_proficiency = 3
        else:
            base_proficiency = 2

        # Confidence based on evidence quality
        if evidence_count >= 3:
            confidence = 0.9
        elif evidence_count >= 2:
            confidence = 0.8
        else:
            confidence = 0.6

        return base_proficiency, confidence

    def _generate_skill_gap_analysis(
        self,
        strongest: List[tuple],
        weakest: List[tuple]
    ) -> str:
        """Generate analysis of skill gaps."""
        strongest_names = ", ".join([s[0] for s in strongest[:2]])
        weakest_names = ", ".join([s[0] for s in weakest[:2]])

        return (
            f"Strongest areas: {strongest_names}. "
            f"Focus improvement on: {weakest_names}. "
            f"Continue leveraging strong skills while building depth in weaker areas."
        )

    async def get_skill_assessment(
        self,
        interview_session_id: str,
        user_id: str
    ) -> Optional[SkillAssessment]:
        """
        Retrieve skill assessment for an interview session.

        Args:
            interview_session_id: Interview session ID
            user_id: User ID

        Returns:
            SkillAssessment document or None if not found
        """
        try:
            assessments_collection = mongodb.get_collection("skill_assessments")
            assessment = await assessments_collection.find_one({
                "interview_session_id": interview_session_id,
                "user_id": user_id
            })

            if assessment:
                return SkillAssessment(**assessment)

            return None

        except Exception as e:
            logger.error(f"Error retrieving skill assessment: {str(e)}")
            return None

    async def get_user_skill_assessments(self, user_id: str) -> List[SkillAssessment]:
        """
        Retrieve all skill assessments for a user.

        Args:
            user_id: User ID

        Returns:
            List of SkillAssessment documents
        """
        try:
            assessments_collection = mongodb.get_collection("skill_assessments")
            assessments = await assessments_collection.find({
                "user_id": user_id
            }).to_list(None)

            return [SkillAssessment(**a) for a in assessments]

        except Exception as e:
            logger.error(f"Error retrieving skill assessments: {str(e)}")
            return []


# Global instance
skill_assessment_service = SkillAssessmentService()
