"""
Resume Repository
Data access layer for resume documents in MongoDB.
"""

import logging
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.database.mongodb import mongodb
from app.database.models.resume import Resume

logger = logging.getLogger(__name__)


class ResumeRepository:
    """Repository for resume data access."""
    
    COLLECTION_NAME = "resumes"
    
    def __init__(self):
        """Initialize resume repository."""
        self.collection = None
        self.logger = logger
    
    async def _get_collection(self):
        """Get the resume collection lazily."""
        if self.collection is None:
            self.collection = mongodb.get_collection(self.COLLECTION_NAME)
        return self.collection
    
    async def create_resume(self, resume_data: Resume) -> str:
        """
        Create a new resume document.
        
        Args:
            resume_data: Resume object to create
            
        Returns:
            ID of created resume
            
        Raises:
            Exception: If creation fails
        """
        try:
            collection = await self._get_collection()
            result = await collection.insert_one(resume_data.dict(by_alias=True))
            self.logger.info(f"Resume created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Failed to create resume: {str(e)}")
            raise
    
    async def get_resume_by_id(self, resume_id: str) -> Optional[Resume]:
        """
        Get resume by ID.
        
        Args:
            resume_id: Resume ID
            
        Returns:
            Resume object or None if not found
        """
        try:
            collection = await self._get_collection()
            resume_doc = await collection.find_one({"_id": ObjectId(resume_id)})
            if resume_doc:
                return Resume(**resume_doc)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get resume {resume_id}: {str(e)}")
            raise
    
    async def get_resumes_by_user(self, user_id: str) -> List[Resume]:
        """
        Get all resumes for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Resume objects
        """
        try:
            collection = await self._get_collection()
            cursor = collection.find({"user_id": user_id})
            resumes = []
            async for doc in cursor:
                resumes.append(Resume(**doc))
            return resumes
        except Exception as e:
            self.logger.error(f"Failed to get resumes for user {user_id}: {str(e)}")
            raise
    
    async def get_primary_resume(self, user_id: str) -> Optional[Resume]:
        """
        Get primary resume for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Primary Resume object or None
        """
        try:
            collection = await self._get_collection()
            resume_doc = await collection.find_one({
                "user_id": user_id,
                "is_primary": True
            })
            if resume_doc:
                return Resume(**resume_doc)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get primary resume for user {user_id}: {str(e)}")
            raise
    
    async def update_resume(self, resume_id: str, update_data: dict) -> Optional[Resume]:
        """
        Update a resume document.
        
        Args:
            resume_id: Resume ID
            update_data: Dictionary of fields to update
            
        Returns:
            Updated Resume object or None if not found
        """
        try:
            # Remove None values from update
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            collection = await self._get_collection()
            result = await collection.find_one_and_update(
                {"_id": ObjectId(resume_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                self.logger.info(f"Resume {resume_id} updated")
                return Resume(**result)
            
            self.logger.warning(f"Resume {resume_id} not found for update")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to update resume {resume_id}: {str(e)}")
            raise
    
    async def update_analysis_status(
        self,
        resume_id: str,
        status: str,
        structured_analysis: Optional[dict] = None,
        error: Optional[str] = None
    ) -> Optional[Resume]:
        """
        Update analysis status and results for a resume.
        
        Args:
            resume_id: Resume ID
            status: New analysis status
            structured_analysis: Analysis result (if completed)
            error: Error message (if failed)
            
        Returns:
            Updated Resume object
        """
        try:
            update_data = {
                "analysis_status": status,
                "analyzed_at": datetime.utcnow() if status == "completed" else None,
            }
            
            if structured_analysis is not None:
                update_data["structured_analysis"] = structured_analysis
            
            if error is not None:
                update_data["analysis_error"] = error
            
            collection = await self._get_collection()
            result = await collection.find_one_and_update(
                {"_id": ObjectId(resume_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                self.logger.info(f"Resume {resume_id} analysis status updated to {status}")
                return Resume(**result)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to update analysis status for {resume_id}: {str(e)}")
            raise
    
    async def update_extracted_text(self, resume_id: str, extracted_text: str) -> Optional[Resume]:
        """
        Update extracted text for a resume.
        
        Args:
            resume_id: Resume ID
            extracted_text: Extracted text from document
            
        Returns:
            Updated Resume object
        """
        try:
            collection = await self._get_collection()
            result = await collection.find_one_and_update(
                {"_id": ObjectId(resume_id)},
                {"$set": {"extracted_text": extracted_text}},
                return_document=True
            )
            
            if result:
                self.logger.info(f"Resume {resume_id} extracted text updated")
                return Resume(**result)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to update extracted text for {resume_id}: {str(e)}")
            raise
    
    async def set_primary_resume(self, user_id: str, resume_id: str) -> bool:
        """
        Set a resume as primary for a user (unset others).
        
        Args:
            user_id: User ID
            resume_id: Resume ID to set as primary
            
        Returns:
            True if successful
        """
        try:
            collection = await self._get_collection()
            # Unset primary on all user's resumes
            await collection.update_many(
                {"user_id": user_id},
                {"$set": {"is_primary": False}}
            )
            
            # Set target resume as primary
            result = await collection.update_one(
                {"_id": ObjectId(resume_id), "user_id": user_id},
                {"$set": {"is_primary": True}}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Resume {resume_id} set as primary for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to set primary resume: {str(e)}")
            raise
    
    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """
        Delete a resume (only if owned by user).
        
        Args:
            resume_id: Resume ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        try:
            collection = await self._get_collection()
            result = await collection.delete_one({
                "_id": ObjectId(resume_id),
                "user_id": user_id
            })
            
            if result.deleted_count > 0:
                self.logger.info(f"Resume {resume_id} deleted for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete resume {resume_id}: {str(e)}")
            raise
    
    async def get_resumes_pending_analysis(self) -> List[Resume]:
        """
        Get all resumes pending analysis.
        
        Args:
            
        Returns:
            List of Resume objects with pending analysis
        """
        try:
            collection = await self._get_collection()
            cursor = collection.find({"analysis_status": "pending"})
            resumes = []
            async for doc in cursor:
                resumes.append(Resume(**doc))
            return resumes
        except Exception as e:
            self.logger.error(f"Failed to get resumes pending analysis: {str(e)}")
            raise
    
    async def count_resumes_by_user(self, user_id: str) -> int:
        """
        Count resumes for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of resumes
        """
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({"user_id": user_id})
            return count
        except Exception as e:
            self.logger.error(f"Failed to count resumes for user {user_id}: {str(e)}")
            raise


# Global repository instance
resume_repository = ResumeRepository()

__all__ = ['ResumeRepository', 'resume_repository']
