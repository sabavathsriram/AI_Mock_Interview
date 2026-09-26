"""
Data Access Layer - Repository Pattern
Provides data access abstractions for MongoDB collections.
"""

from app.database.repositories.resume_repository import (
    ResumeRepository,
    resume_repository,
)

__all__ = [
    'ResumeRepository',
    'resume_repository',
]
