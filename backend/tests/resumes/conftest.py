"""
Pytest configuration for resume tests.
"""

import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.database.mongodb import mongodb


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_database():
    """Setup test database for each test function."""
    # Connect to test database
    test_db_name = f"test_{settings.MONGODB_DB_NAME}"
    test_client = AsyncIOMotorClient(settings.MONGODB_URI)
    test_db = test_client[test_db_name]
    
    # Store original database reference
    original_db = mongodb.database
    
    # Replace with test database
    mongodb.database = test_db
    
    # Clear test collections
    await test_db.users.delete_many({})
    await test_db.resume_documents.delete_many({})
    
    yield test_db
    
    # Restore original database
    mongodb.database = original_db
    
    # Clean up test database
    await test_client.drop_database(test_db_name)
    test_client.close()
