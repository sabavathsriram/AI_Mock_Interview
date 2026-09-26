"""
Manual authentication tests.
"""

import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1/auth"

async def test_endpoint(url, method="GET", json=None, headers=None):
    """Test an endpoint."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=json, headers=headers)
            else:
                return None, f"Unsupported method: {method}"
            
            return response.status_code, response.json() if response.content else None
        except Exception as e:
            return None, str(e)

async def run_tests():
    """Run authentication tests."""
    print("=" * 60)
    print("AUTHENTICATION TESTS")
    print("=" * 60)
    
    # Test 1: Auth health endpoint
    print("\n1. Testing auth health endpoint...")
    status, data = await test_endpoint(f"{BASE_URL}/health")
    if status == 200:
        print(f"   ✓ PASS: Status {status}, Data: {data}")
    else:
        print(f"   ✗ FAIL: Status {status}, Error: {data}")
    
    # Test 2: User registration
    print("\n2. Testing user registration...")
    import uuid
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    user_data = {
        "email": unique_email,
        "full_name": "Test User",
        "password": "TestPass123!"
    }
    status, data = await test_endpoint(f"{BASE_URL}/register", "POST", user_data)
    if status == 201:
        print(f"   ✓ PASS: User registered successfully")
        user_id = data.get("id")
        email = data.get("email")
    else:
        print(f"   ✗ FAIL: Could not register user: {data}")
        return
    
    # Test 3: Duplicate registration
    print("\n3. Testing duplicate registration...")
    status, data = await test_endpoint(f"{BASE_URL}/register", "POST", user_data)
    if status == 400 and "already exists" in str(data):
        print(f"   ✓ PASS: Duplicate registration rejected as expected")
    else:
        print(f"   ✗ FAIL: Expected duplicate rejection, got status {status}: {data}")
    
    # Test 4: Successful login
    print("\n4. Testing successful login...")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    status, data = await test_endpoint(f"{BASE_URL}/login", "POST", login_data)
    if status == 200 and "access_token" in data:
        print(f"   ✓ PASS: Login successful, got access token")
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"   ✗ FAIL: Login failed: {data}")
        return
    
    # Test 5: Invalid password login
    print("\n5. Testing invalid password login...")
    invalid_login = {
        "email": user_data["email"],
        "password": "WrongPassword123!"
    }
    status, data = await test_endpoint(f"{BASE_URL}/login", "POST", invalid_login)
    if status == 401:
        print(f"   ✓ PASS: Invalid password rejected as expected")
    else:
        print(f"   ✗ FAIL: Expected 401 for invalid password, got {status}: {data}")
    
    # Test 6: Protected endpoint with valid token
    print("\n6. Testing protected endpoint with valid token...")
    status, data = await test_endpoint(f"{BASE_URL}/me", "GET", headers=headers)
    if status == 200 and data.get("email") == user_data["email"]:
        print(f"   ✓ PASS: Protected endpoint accessible with valid token")
    else:
        print(f"   ✗ FAIL: Protected endpoint failed: {data}")
    
    # Test 7: Protected endpoint without token
    print("\n7. Testing protected endpoint without token...")
    status, data = await test_endpoint(f"{BASE_URL}/me", "GET")
    if status in [401, 403]:
        print(f"   ✓ PASS: Protected endpoint rejected without token (status {status})")
    else:
        print(f"   ✗ FAIL: Expected rejection without token, got {status}: {data}")
    
    # Test 8: Protected test endpoint
    print("\n8. Testing protected test endpoint...")
    status, data = await test_endpoint(f"{BASE_URL}/protected-test", "GET", headers=headers)
    if status == 200 and data.get("message") == "This is a protected endpoint":
        print(f"   ✓ PASS: Protected test endpoint works")
    else:
        print(f"   ✗ FAIL: Protected test endpoint failed: {data}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("All authentication tests completed!")

if __name__ == "__main__":
    # Give server time to start
    import time
    print("Waiting for server to start...")
    time.sleep(2)
    
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests interrupted")
    except Exception as e:
        print(f"\nError running tests: {e}")
        sys.exit(1)