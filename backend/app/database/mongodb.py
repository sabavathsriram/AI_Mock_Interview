"""
MongoDB database connection module.
"""

import motor.motor_asyncio
from app.core.config import settings


class MongoDB:
    """MongoDB database connection manager."""
    
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    database: motor.motor_asyncio.AsyncIOMotorDatabase = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB database."""
        if cls.client is None:
            cls.client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URI,
                maxPoolSize=10,
                minPoolSize=1
            )
            cls.database = cls.client[settings.MONGODB_DB_NAME]
            print(f"Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB database."""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.database = None
            print("Disconnected from MongoDB")
    
    @classmethod
    def get_database(cls) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.database
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection from the database."""
        return cls.get_database()[collection_name]


# Global database instance
mongodb = MongoDB()