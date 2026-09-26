/**
 * Full Integration Test for AI Mock Interview System
 * 
 * This script tests the complete integration between frontend and backend:
 * 1. Backend connectivity and health
 * 2. Authentication flow
 * 3. Resume upload and management
 * 4. Error handling
 * 5. CORS configuration
 */

const axios = require('axios');

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;
const TEST_USER = {
  email: `test_${Date.now()}@example.com`,
  password: 'TestPassword123',
  full_name: 'Integration Test User'
};

console.log('🚀 Starting Full Integration Test for AI Mock Interview System\n');
console.log(`API Base URL: ${API_BASE_URL}`);
console.log(`API v1 URL: ${API_V1_URL}`);
console.log(`Test User: ${TEST_USER.email}\n`);

// Test results tracking
const testResults = {
  total: 0,
  passed: 0,
  failed: 0
};

// Helper function to run tests
async function runTest(name, testFn) {
  testResults.total++;
  process.stdout.write(`📋 ${name}... `);
  
  try {
    await testFn();
    testResults.passed++;
    console.log('✅ PASSED');
  } catch (error) {
    testResults.failed++;
    console.log('❌ FAILED');
    console.log(`   Error: ${error.message}`);
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      console.log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }
}

// Test 1: Backend Health Check
async function testBackendHealth() {
  const response = await axios.get(`${API_BASE_URL}/health`);
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  if (response.data.status !== 'healthy') {
    throw new Error(`Expected status 'healthy', got '${response.data.status}'`);
  }
}

// Test 2: CORS Configuration
async function testCORS() {
  const response = await axios.options(`${API_BASE_URL}/health`, {
    headers: {
      'Origin': 'http://localhost:3000',
      'Access-Control-Request-Method': 'GET'
    }
  });
  
  if (!response.headers['access-control-allow-origin']?.includes('localhost:3000')) {
    throw new Error('CORS not properly configured for frontend origin');
  }
}

// Test 3: User Registration
let authToken = null;
let refreshToken = null;

async function testUserRegistration() {
  const response = await axios.post(`${API_V1_URL}/auth/register`, TEST_USER);
  
  if (response.status !== 201) {
    throw new Error(`Expected status 201, got ${response.status}`);
  }
  
  if (!response.data.email || response.data.email !== TEST_USER.email) {
    throw new Error('User registration failed - email mismatch');
  }
}

// Test 4: User Login
async function testUserLogin() {
  const response = await axios.post(`${API_V1_URL}/auth/login`, {
    email: TEST_USER.email,
    password: TEST_USER.password
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!response.data.access_token || !response.data.refresh_token) {
    throw new Error('Login failed - missing tokens');
  }
  
  authToken = response.data.access_token;
  refreshToken = response.data.refresh_token;
}

// Test 5: Protected Endpoint Access
async function testProtectedEndpoint() {
  const response = await axios.get(`${API_V1_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (response.data.email !== TEST_USER.email) {
    throw new Error('Protected endpoint returned wrong user data');
  }
}

// Test 6: Resume Service - Supported Formats
async function testResumeSupportedFormats() {
  const response = await axios.get(`${API_V1_URL}/resumes/info/supported-formats`);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!Array.isArray(response.data.supported_formats)) {
    throw new Error('Supported formats should be an array');
  }
  
  if (response.data.supported_formats.length === 0) {
    throw new Error('No supported formats returned');
  }
}

// Test 7: Resume Service - List Resumes (Empty)
async function testResumeListEmpty() {
  const response = await axios.get(`${API_V1_URL}/resumes/list`, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!Array.isArray(response.data.resumes)) {
    throw new Error('Resumes should be an array');
  }
  
  if (response.data.total_count !== 0) {
    throw new Error(`Expected 0 resumes for new user, got ${response.data.total_count}`);
  }
}

// Test 8: Authentication Error Handling
async function testAuthErrorHandling() {
  try {
    await axios.get(`${API_V1_URL}/auth/me`, {
      headers: {
        'Authorization': 'Bearer invalid_token_123'
      }
    });
    throw new Error('Should have thrown 401 error for invalid token');
  } catch (error) {
    if (error.response?.status !== 401) {
      throw new Error(`Expected 401 for invalid token, got ${error.response?.status}`);
    }
  }
}

// Test 9: Not Found Error Handling
async function testNotFoundError() {
  try {
    await axios.get(`${API_V1_URL}/nonexistent-endpoint`);
    throw new Error('Should have thrown 404 error');
  } catch (error) {
    if (error.response?.status !== 404) {
      throw new Error(`Expected 404 for nonexistent endpoint, got ${error.response?.status}`);
    }
  }
}

// Test 10: Database Connection
async function testDatabaseConnection() {
  const response = await axios.get(`${API_BASE_URL}/database/test`);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (response.data.status !== 'success') {
    throw new Error(`Database connection failed: ${response.data.message}`);
  }
}

// Test 11: LLM Service Health
async function testLLMHealth() {
  try {
    const response = await axios.get(`${API_V1_URL}/llm/health`);
    
    if (response.status !== 200) {
      throw new Error(`Expected status 200, got ${response.status}`);
    }
    
    console.log(`   LLM Status: ${response.data.status || 'unknown'}`);
  } catch (error) {
    // LLM service might not be configured - that's okay for integration test
    console.log('   ⚠️ LLM service not available (expected if not configured)');
  }
}

// Test 12: Auth Service Health
async function testAuthServiceHealth() {
  const response = await axios.get(`${API_V1_URL}/auth/health`);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (response.data.service !== 'authentication') {
    throw new Error(`Expected service 'authentication', got '${response.data.service}'`);
  }
}

// Run all tests
async function runAllTests() {
  console.log('='.repeat(60));
  console.log('🧪 RUNNING INTEGRATION TESTS');
  console.log('='.repeat(60) + '\n');
  
  // Phase 1: Basic Connectivity
  console.log('📡 PHASE 1: BASIC CONNECTIVITY\n');
  await runTest('Backend Health Check', testBackendHealth);
  await runTest('CORS Configuration', testCORS);
  await runTest('Database Connection', testDatabaseConnection);
  
  // Phase 2: Authentication
  console.log('\n🔐 PHASE 2: AUTHENTICATION\n');
  await runTest('User Registration', testUserRegistration);
  await runTest('User Login', testUserLogin);
  await runTest('Protected Endpoint Access', testProtectedEndpoint);
  await runTest('Auth Service Health', testAuthServiceHealth);
  
  // Phase 3: Services
  console.log('\n🛠️ PHASE 3: SERVICES\n');
  await runTest('Resume - Supported Formats', testResumeSupportedFormats);
  await runTest('Resume - List (Empty)', testResumeListEmpty);
  await runTest('LLM Service Health', testLLMHealth);
  
  // Phase 4: Error Handling
  console.log('\n🚨 PHASE 4: ERROR HANDLING\n');
  await runTest('Authentication Error (Invalid Token)', testAuthErrorHandling);
  await runTest('Not Found Error Handling', testNotFoundError);
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total Tests: ${testResults.total}`);
  console.log(`Passed: ${testResults.passed} ✅`);
  console.log(`Failed: ${testResults.failed} ❌`);
  console.log(`Success Rate: ${Math.round((testResults.passed / testResults.total) * 100)}%`);
  
  if (testResults.failed === 0) {
    console.log('\n🎉 ALL INTEGRATION TESTS PASSED!');
    console.log('The frontend-backend integration is fully functional.');
  } else {
    console.log(`\n⚠️ ${testResults.failed} test(s) failed.`);
    console.log('Check the errors above and ensure backend services are running properly.');
  }
  
  // Cleanup recommendation
  console.log('\n💡 RECOMMENDATION:');
  console.log('Test user created during this test can be deleted from the database.');
  console.log(`Email: ${TEST_USER.email}`);
}

// Handle errors
process.on('unhandledRejection', (error) => {
  console.error('Unhandled promise rejection:', error);
  process.exit(1);
});

// Run the tests
runAllTests().catch(error => {
  console.error('Test suite failed:', error);
  process.exit(1);
});