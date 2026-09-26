"""
Authentication tests for the AI-Powered Mock Interview System.
"""

import pytest
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.core.config import settings
from app.database.mongodb import mongodb


# Test user data
TEST_USER = {
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "TestPass123!"
}

# Test user data for duplicate registration
TEST_USER_DUPLICATE = {
    "email": "test2@example.com",
    "full_name": "Test User 2",
    "password": "TestPass123!"
}

# Invalid password data
INVALID_PASSWORD_USER = {
    "email": "invalid@example.com",
    "full_name": "Invalid User",
    "password": "short"
}

# Login test data
LOGIN_DATA = {
    "email": "test@example.com",
    "password": "TestPass123!"
}

# Invalid login data
INVALID_LOGIN_DATA = {
    "email": "test@example.com",
    "password": "WrongPassword123!"
}

# Non-existent user login
NONEXISTENT_LOGIN_DATA = {
    "email": "nonexistent@example.com",
    "password": "SomePass123!"
}


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test module."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    """Setup and teardown for tests."""
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
    
    yield
    
    # Restore original database
    mongodb.database = original_db
    
    # Clean up test database
    await test_client.drop_database(test_db_name)
    test_client.close()


class TestAuthentication:
    """Test authentication functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_registration(self, async_client: AsyncClient):
        """Test successful user registration."""
        response = await async_client.post("/api/v1/auth/register", json=TEST_USER)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["email"] == TEST_USER["email"]
        assert data["full_name"] == TEST_USER["full_name"]
        assert data["role"] == "candidate"
        assert data["is_active"] is True
        assert "created_at" in data
        assert "updated_at" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    @pytest.mark.asyncio
    async def test_duplicate_registration(self, async_client: AsyncClient):
        """Test duplicate user registration."""
        # First registration
        response1 = await async_client.post("/api/v1/auth/register", json=TEST_USER_DUPLICATE)
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = await async_client.post("/api/v1/auth/register", json=TEST_USER_DUPLICATE)
        
        assert response2.status_code == 400
        data = response2.json()
        assert "already exists" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_password_registration(self, async_client: AsyncClient):
        """Test registration with invalid password."""
        response = await async_client.post("/api/v1/auth/register", json=INVALID_PASSWORD_USER)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_successful_login(self, async_client: AsyncClient):
        """Test successful user login."""
        # First register a user
        response1 = await async_client.post("/api/v1/auth/register", json=TEST_USER)
        assert response1.status_code == 201
        
        # Then login
        response2 = await async_client.post("/api/v1/auth/login", json=LOGIN_DATA)
        
        assert response2.status_code == 200
        data = response2.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    @pytest.mark.asyncio
    async def test_invalid_password_login(self, async_client: AsyncClient):
        """Test login with invalid password."""
        # First register a user
        response1 = await async_client.post("/api/v1/auth/register", json=TEST_USER)
        assert response1.status_code == 201
        
        # Then try to login with wrong password
        response2 = await async_client.post("/api/v1/auth/login", json=INVALID_LOGIN_DATA)
        
        assert response2.status_code == 401
        data = response2.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower() or "invalid" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_nonexistent_user_login(self, async_client: AsyncClient):
        """Test login with non-existent user."""
        response = await async_client.post("/api/v1/auth/login", json=NONEXISTENT_LOGIN_DATA)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower() or "invalid" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint with valid token."""
        # Register and login
        response1 = await async_client.post("/api/v1/auth/register", json=TEST_USER)
        assert response1.status_code == 201
        
        response2 = await async_client.post("/api/v1/auth/login", json=LOGIN_DATA)
        assert response2.status_code == 200
        
        token_data = response2.json()
        access_token = token_data["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response3 = await async_client.get("/api/v1/auth/me", headers=headers)
        
        assert response3.status_code == 200
        data = response3.json()
        
        assert data["email"] == TEST_USER["email"]
        assert data["full_name"] == TEST_USER["full_name"]
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await async_client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden - no token provided
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401  # Unauthorized - invalid token
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_protected_test_endpoint(self, async_client: AsyncClient):
        """Test the protected test endpoint."""
        # Register and login
        response1 = await async_client.post("/api/v1/auth/register", json=TEST_USER)
        assert response1.status_code == 201
        
        response2 = await async_client.post("/api/v1/auth/login", json=LOGIN_DATA)
        assert response2.status_code == 200
        
        token_data = response2.json()
        access_token = token_data["access_token"]
        
        # Access protected test endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response3 = await async_client.get("/api/v1/auth/protected-test", headers=headers)
        
        assert response3.status_code == 200
        data = response3.json()
        
        assert data["message"] == "This is a protected endpoint"
        assert "user_id" in data
        assert data["email"] == TEST_USER["email"]
        assert data["role"] == "candidate"
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, async_client: AsyncClient):
        """Test token refresh functionality."""
        # Register and login
        response1 = await async_client.post("/api/v1/auth/register", json=TEST_USER)
        assert response1.status_code == 201
        
        response2 = await async_client.post("/api/v1/auth/login", json=LOGIN_DATA)
        assert response2.status_code == 200
        
        token_data = response2.json()
        refresh_token = token_data["refresh_token"]
        
        # Refresh token
        response3 = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response3.status_code == 200
        new_token_data = response3.json()
        
        assert "access_token" in new_token_data
        assert "refresh_token" in new_token_data
        assert new_token_data["access_token"] != token_data["access_token"]
        assert new_token_data["refresh_token"] != token_data["refresh_token"]
    
    @pytest.mark.asyncio
    async def test_auth_health_endpoint(self, async_client: AsyncClient):
        """Test authentication health endpoint."""
        response = await async_client.get("/api/v1/auth/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "authentication"