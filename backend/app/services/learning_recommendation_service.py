"""
Learning Recommendation Service for generating personalized learning paths.
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from app.database.mongodb import mongodb
from app.database.models.learning_recommendation import (
    LearningRecommendation,
    LearningResource,
    LearningPath,
    ResourceType,
    DifficultyLevel
)

logger = logging.getLogger(__name__)


class LearningRecommendationService:
    """Service for generating personalized learning recommendations."""

    # Curated learning resources library
    RESOURCE_LIBRARY = {
        "Python": [
            LearningResource(
                title="Python for Data Science and Machine Learning",
                resource_type=ResourceType.COURSE,
                url="https://www.coursera.org/learn/python-data-analysis",
                description="Complete Python course for data science",
                estimated_time_hours=40,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                free_resource=False,
                skills_covered=["Python", "Data Analysis"],
                rating=4.7,
                review_count=15000,
                source="Coursera",
                relevance_score=0.9
            ),
            LearningResource(
                title="Real Python Tutorials",
                resource_type=ResourceType.ARTICLE,
                url="https://realpython.com/",
                description="In-depth Python tutorials and guides",
                estimated_time_hours=2,
                difficulty_level=DifficultyLevel.BEGINNER,
                free_resource=True,
                skills_covered=["Python"],
                rating=4.8,
                review_count=5000,
                source="Real Python",
                relevance_score=0.85
            ),
        ],
        "System Design": [
            LearningResource(
                title="System Design Interview Course",
                resource_type=ResourceType.COURSE,
                url="https://www.educative.io/courses/grokking-the-system-design-interview",
                description="Complete system design interview preparation",
                estimated_time_hours=30,
                difficulty_level=DifficultyLevel.ADVANCED,
                free_resource=False,
                skills_covered=["System Design", "Architecture", "Scalability"],
                rating=4.6,
                review_count=8000,
                source="Educative",
                relevance_score=0.95
            ),
            LearningResource(
                title="Designing Microservices",
                resource_type=ResourceType.BOOK,
                url="https://www.oreilly.com/library/view/designing-microservices/",
                description="Practical guide to microservices architecture",
                estimated_time_hours=15,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                free_resource=False,
                skills_covered=["System Design", "Microservices"],
                rating=4.5,
                source="O'Reilly",
                relevance_score=0.9
            ),
        ],
        "Data Structures": [
            LearningResource(
                title="Data Structures and Algorithms Masterclass",
                resource_type=ResourceType.COURSE,
                url="https://www.udemy.com/course/data-structures-algorithms/",
                description="Complete DSA course with practice problems",
                estimated_time_hours=50,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                free_resource=False,
                skills_covered=["Data Structures", "Algorithms"],
                rating=4.7,
                review_count=20000,
                source="Udemy",
                relevance_score=0.95
            ),
            LearningResource(
                title="LeetCode Premium",
                resource_type=ResourceType.PRACTICE_EXERCISE,
                url="https://leetcode.com/",
                description="Practice coding problems for interviews",
                estimated_time_hours=5,
                difficulty_level=DifficultyLevel.BEGINNER,
                free_resource=False,
                skills_covered=["Data Structures", "Algorithms", "Coding"],
                rating=4.6,
                review_count=50000,
                source="LeetCode",
                relevance_score=0.9
            ),
        ],
        "Communication": [
            LearningResource(
                title="Effective Communication for Technical Professionals",
                resource_type=ResourceType.COURSE,
                url="https://www.coursera.org/learn/communication",
                description="Improve communication and presentation skills",
                estimated_time_hours=15,
                difficulty_level=DifficultyLevel.BEGINNER,
                free_resource=True,
                skills_covered=["Communication", "Presentation"],
                rating=4.5,
                review_count=5000,
                source="Coursera",
                relevance_score=0.85
            ),
        ],
        "JavaScript": [
            LearningResource(
                title="The Complete JavaScript Course",
                resource_type=ResourceType.COURSE,
                url="https://www.udemy.com/course/the-complete-javascript-course/",
                description="Modern JavaScript from basics to advanced",
                estimated_time_hours=69,
                difficulty_level=DifficultyLevel.BEGINNER,
                free_resource=False,
                skills_covered=["JavaScript", "Web Development"],
                rating=4.7,
                review_count=30000,
                source="Udemy",
                relevance_score=0.9
            ),
        ],
    }

    async def generate_learning_recommendations(
        self,
        interview_session_id: str,
        user_id: str,
        skill_assessment_id: Optional[str] = None,
        evaluation_id: Optional[str] = None,
    ) -> Optional[List[LearningRecommendation]]:
        """
        Generate learning recommendations based on interview performance.

        Args:
            interview_session_id: ID of the interview session
            user_id: ID of the user
            skill_assessment_id: Optional reference to skill assessment
            evaluation_id: Optional reference to evaluation

        Returns:
            List of LearningRecommendation documents if successful
        """
        try:
            # Fetch skill assessment to get weakest skills
            skill_assessments_collection = mongodb.get_collection("skill_assessments")
            skill_assessment = await skill_assessments_collection.find_one({
                "_id": skill_assessment_id
            }) if skill_assessment_id else None

            if not skill_assessment:
                # Try to find by session
                skill_assessment = await skill_assessments_collection.find_one({
                    "interview_session_id": interview_session_id,
                    "user_id": user_id
                })

            if not skill_assessment:
                logger.warning(f"No skill assessment found for session {interview_session_id}")
                return None

            # Get weakest skills to focus on
            weakest_skills = skill_assessment.get("weakest_skills", [])
            skill_gaps = skill_assessment.get("recommended_skill_focus", [])

            if not skill_gaps:
                skill_gaps = weakest_skills

            logger.info(f"Generating recommendations for skill gaps: {skill_gaps}")

            recommendations: List[LearningRecommendation] = []

            # Generate recommendation for each skill gap
            for priority, skill in enumerate(skill_gaps[:3], 1):  # Top 3 gaps
                resources = self._curate_resources_for_skill(skill)

                if resources:
                    # Create learning paths
                    learning_paths = []
                    if len(resources) > 1:
                        # Beginner resources first, then advanced
                        path = LearningPath(
                            name=f"{skill} Mastery Path",
                            description=f"Complete learning path for mastering {skill}",
                            target_skill=skill,
                            total_estimated_time_hours=sum(
                                r.estimated_time_hours or 10 for r in resources
                            ),
                            resources=resources,
                            order=list(range(len(resources))),
                        )
                        learning_paths.append(path)

                    # Create recommendation
                    recommendation = LearningRecommendation(
                        user_id=user_id,
                        interview_session_id=interview_session_id,
                        skill_assessment_id=skill_assessment_id,
                        evaluation_id=evaluation_id,
                        title=f"Improve {skill}",
                        description=f"Based on your interview performance, focusing on {skill} will improve your technical profile.",
                        priority_level=(5 - priority),  # Higher priority for more important gaps
                        target_skills=[skill],
                        skill_gaps_addressed=[skill],
                        resources=resources,
                        learning_paths=learning_paths,
                        estimated_completion_time_hours=sum(
                            r.estimated_time_hours or 10 for r in resources
                        ),
                        recommended_start_date=datetime.utcnow(),
                        recommended_completion_date=datetime.utcnow() + timedelta(days=30 * priority),
                        is_ai_generated=True,
                        ai_model_used="gemini",
                        confidence_score=0.85,
                    )

                    recommendations.append(recommendation)

            # Store recommendations in MongoDB
            if recommendations:
                recommendations_collection = mongodb.get_collection("learning_recommendations")

                for rec in recommendations:
                    result = await recommendations_collection.insert_one(rec.dict(by_alias=True))
                    logger.info(f"Stored learning recommendation {str(result.inserted_id)}")

                # Update interview session with recommendations reference
                interviews_collection = mongodb.get_collection("interviews")
                from bson import ObjectId
                await interviews_collection.update_one(
                    {"_id": ObjectId(interview_session_id)},
                    {
                        "$set": {
                            "has_recommendations": True,
                        }
                    }
                )

                logger.info(
                    f"Generated {len(recommendations)} learning recommendations "
                    f"for session {interview_session_id}"
                )

                return recommendations

            return None

        except Exception as e:
            logger.error(f"Error generating learning recommendations: {str(e)}", exc_info=True)
            return None

    def _curate_resources_for_skill(self, skill: str) -> List[LearningResource]:
        """
        Curate learning resources for a specific skill.

        Args:
            skill: Skill name

        Returns:
            List of LearningResource objects
        """
        # Check if we have resources for this exact skill
        if skill in self.RESOURCE_LIBRARY:
            return self.RESOURCE_LIBRARY[skill]

        # Try to find similar skills (partial match)
        for lib_skill, resources in self.RESOURCE_LIBRARY.items():
            if skill.lower() in lib_skill.lower() or lib_skill.lower() in skill.lower():
                return resources

        # Fallback: return generic development resources
        return [
            LearningResource(
                title=f"Learn {skill} - Comprehensive Guide",
                resource_type=ResourceType.COURSE,
                url=f"https://www.udemy.com/courses/search/?q={skill}",
                description=f"Find courses and materials for {skill} on Udemy",
                estimated_time_hours=20,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                free_resource=False,
                skills_covered=[skill],
                rating=4.5,
                source="Udemy",
                relevance_score=0.7
            ),
            LearningResource(
                title=f"{skill} Documentation",
                resource_type=ResourceType.ARTICLE,
                url=f"https://www.google.com/search?q={skill}+documentation",
                description=f"Official documentation and guides for {skill}",
                estimated_time_hours=5,
                difficulty_level=DifficultyLevel.BEGINNER,
                free_resource=True,
                skills_covered=[skill],
                rating=4.3,
                source="Official Docs",
                relevance_score=0.8
            ),
        ]

    async def get_learning_recommendations(
        self,
        interview_session_id: str,
        user_id: str
    ) -> List[LearningRecommendation]:
        """
        Retrieve learning recommendations for an interview session.

        Args:
            interview_session_id: Interview session ID
            user_id: User ID

        Returns:
            List of LearningRecommendation documents
        """
        try:
            recommendations_collection = mongodb.get_collection("learning_recommendations")
            recommendations = await recommendations_collection.find({
                "interview_session_id": interview_session_id,
                "user_id": user_id
            }).to_list(None)

            return [LearningRecommendation(**r) for r in recommendations]

        except Exception as e:
            logger.error(f"Error retrieving learning recommendations: {str(e)}")
            return []

    async def get_user_learning_recommendations(self, user_id: str) -> List[LearningRecommendation]:
        """
        Retrieve all learning recommendations for a user.

        Args:
            user_id: User ID

        Returns:
            List of LearningRecommendation documents
        """
        try:
            recommendations_collection = mongodb.get_collection("learning_recommendations")
            recommendations = await recommendations_collection.find({
                "user_id": user_id
            }).to_list(None)

            return [LearningRecommendation(**r) for r in recommendations]

        except Exception as e:
            logger.error(f"Error retrieving user learning recommendations: {str(e)}")
            return []


# Global instance
learning_recommendation_service = LearningRecommendationService()
