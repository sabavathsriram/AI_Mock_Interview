# API Service Layer Documentation

## Overview

The API service layer provides a comprehensive TypeScript client for interacting with the AI Mock Interview System backend. It includes 6 main service classes with proper TypeScript interfaces, axios interceptors for authentication, error handling, and both real implementations for existing endpoints and placeholder implementations for missing endpoints.

## Services

### 1. AuthService (`authService`)
Handles user authentication and authorization.

**Methods:**
- `login(credentials: LoginRequest): Promise<ApiResponse<TokenResponse>>` - User login
- `register(userData: RegisterRequest): Promise<ApiResponse<UserResponse>>` - User registration
- `refreshToken(refreshToken: string): Promise<ApiResponse<TokenResponse>>` - Refresh access token
- `getCurrentUser(): Promise<ApiResponse<UserResponse>>` - Get current user info
- `changePassword(data: ChangePasswordRequest): Promise<ApiResponse<{ message: string }>>` - Change password
- `logout(): Promise<void>` - Logout user
- `isAuthenticated(): Promise<boolean>` - Check authentication status

**Interfaces:**
```typescript
interface LoginRequest { email: string; password: string; }
interface RegisterRequest { email: string; full_name: string; password: string; }
interface UserResponse { id: string; email: string; full_name: string; role: string; is_active: boolean; timestamps; }
interface TokenResponse { access_token: string; refresh_token: string; token_type: string; expires_in: number; }
```

### 2. ResumeService (`resumeService`)
Manages resume uploads, listing, and processing.

**Methods:**
- `uploadResume(file: File, displayName?: string, isPrimary?: boolean, onProgress?: (progress: UploadProgress) => void): Promise<ApiResponse<ResumeUploadResponse>>` - Upload resume
- `listResumes(): Promise<ApiResponse<ResumeListResponse>>` - List user's resumes
- `getResume(resumeId: string): Promise<ApiResponse<ResumeDetailResponse>>` - Get resume details
- `deleteResume(resumeId: string): Promise<ApiResponse<{ success: boolean; message: string }>>` - Delete resume
- `getResumeText(resumeId: string): Promise<ApiResponse<{...}>>` - Get extracted text
- `getSupportedFormats(): Promise<ApiResponse<FileSupportInfo>>` - Get supported formats
- `validateFile(file: File): Promise<{ valid: boolean; error?: string }>` - Validate file before upload

**Interfaces:** See `api.ts` for complete type definitions.

### 3. ResumeAnalysisService (`resumeAnalysisService`)
Handles AI-powered resume analysis and intelligence.

**Methods:**
- `analyzeResume(request: ResumeAnalysisRequest): Promise<ApiResponse<ResumeAnalysisResponse>>` - Trigger AI analysis
- `getAnalysisResults(resumeId: string): Promise<ApiResponse<ResumeAnalysisResponse>>` - Get analysis results
- `getAnalysisStatus(resumeId: string): Promise<ApiResponse<{...}>>` - Get analysis status
- `getAnalysisSummary(resumeId: string): Promise<ApiResponse<ResumeAnalysisSummary>>` - Get analysis summary

### 4. InterviewService (`interviewService`)
Manages mock interview sessions, questions, and evaluations.

**Note:** Backend endpoints are currently placeholders. Service returns mock data.

**Methods:**
- `getInterviewTemplates(): Promise<ApiResponse<InterviewTemplate[]>>` - Get available templates
- `startInterview(data: { template_id?: string; resume_id?: string; title?: string; custom_settings?: any }): Promise<ApiResponse<InterviewSession>>` - Start new interview
- `getInterviewSession(sessionId: string): Promise<ApiResponse<InterviewSession>>` - Get session details
- `getNextQuestion(sessionId: string): Promise<ApiResponse<InterviewQuestion>>` - Get next question
- `submitAnswer(sessionId: string, questionId: string, answer: InterviewAnswer): Promise<ApiResponse<{...}>>` - Submit answer
- `completeInterview(sessionId: string): Promise<ApiResponse<InterviewEvaluation>>` - Complete interview
- `getInterviewHistory(params?: { page?: number; page_size?: number; status?: string }): Promise<ApiResponse<PaginatedResponse<InterviewSession>>>` - Get interview history
- `getInterviewEvaluation(sessionId: string): Promise<ApiResponse<InterviewEvaluation>>` - Get evaluation results

### 5. UserService (`userService`)
Manages user profiles, settings, and statistics.

**Note:** Backend endpoints are currently placeholders. Service returns mock data.

**Methods:**
- `getUserProfile(): Promise<ApiResponse<UserProfile>>` - Get user profile
- `updateUserProfile(profile: Partial<UserProfile>): Promise<ApiResponse<UserProfile>>` - Update profile
- `getUserStats(): Promise<ApiResponse<UserStats>>` - Get user statistics
- `updateNotificationSettings(settings: Partial<UserProfile['notification_settings']>): Promise<ApiResponse<UserProfile>>` - Update notification settings

### 6. SystemService (`systemService`)
Handles system health checks and monitoring.

**Methods:**
- `getSystemHealth(): Promise<ApiResponse<SystemHealth>>` - Get system health
- `getDatabaseStatus(): Promise<ApiResponse<{ status: string; message: string }>>` - Check database status
- `getLLMHealth(): Promise<ApiResponse<LLMHealth>>` - Check LLM service health

## BaseService Class

All services extend the `BaseService` class which provides:
- Common HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Error handling through axios interceptors
- Authentication token injection
- Consistent response formatting

## Error Handling

The API layer includes comprehensive error handling:

### Error Types
- `NETWORK` - Network connectivity issues
- `TIMEOUT` - Request timeout
- `UNAUTHORIZED` - Authentication required (401)
- `FORBIDDEN` - Insufficient permissions (403)
- `NOT_FOUND` - Resource not found (404)
- `VALIDATION` - Input validation errors (400, 422)
- `SERVER` - Server errors (500+)
- `UNKNOWN` - Other errors

### Error Format
All errors are standardized to:
```typescript
interface ApiError {
  type: ErrorType;
  message: string;
  status?: number;
  data?: any;
  originalError?: any;
}
```

### Axios Interceptors
1. **Request Interceptor**: Injects authentication token
2. **Response Interceptor**: 
   - Handles token refresh on 401 errors
   - Standardizes error responses
   - Provides user-friendly error messages

## Custom React Hooks

### `useApi<T>` Hook
For data fetching with loading and error states:
```typescript
const { data, isLoading, error, fetchData, reset } = useApi<T>(
  fetchFn: () => Promise<T>,
  options?: UseApiOptions<T>
);
```

### `useApiMutation<T, R>` Hook
For API mutations (POST, PUT, DELETE):
```typescript
const { data, isLoading, error, mutate, reset } = useApiMutation<T, R>(
  mutationFn: (data: T) => Promise<R>,
  options?: { onSuccess?, onError? }
);
```

## Usage Examples

### Basic Data Fetching
```typescript
import { userService } from '@/services/api';
import { useApi } from '@/hooks/useApi';

const ProfileComponent = () => {
  const { data: profile, isLoading, error } = useApi(
    () => userService.getUserProfile().then(res => res.data),
    { immediate: true }
  );
  
  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return <ProfileDisplay profile={profile} />;
};
```

### Form Submission with Mutation
```typescript
import { authService } from '@/services/api';
import { useApiMutation } from '@/hooks/useApi';

const LoginForm = () => {
  const { mutate, isLoading, error } = useApiMutation(
    (credentials) => authService.login(credentials).then(res => res.data),
    {
      onSuccess: (tokens) => {
        setAuthTokens(tokens);
        navigate('/dashboard');
      }
    }
  );
  
  const handleSubmit = (data) => {
    mutate(data);
  };
  
  return (
    <Form onSubmit={handleSubmit} isLoading={isLoading}>
      {error && <ErrorAlert message={error.message} />}
      {/* form fields */}
    </Form>
  );
};
```

## Configuration

### Environment Variables
- `VITE_API_BASE_URL`: API base URL (default: `http://localhost:8000/api/v1`)

### Axios Configuration
- Base URL: From environment variable
- Timeout: 30 seconds
- Headers: `Content-Type: application/json`
- Authentication: Bearer token from localStorage

## Authentication Flow

1. User logs in with `authService.login()`
2. Tokens are stored in localStorage
3. Request interceptor adds token to all subsequent requests
4. On 401 errors, interceptor attempts token refresh
5. If refresh fails, user is redirected to login

## Development Notes

### Mock Data
For endpoints that are not yet implemented in the backend, services return mock data that matches the expected structure. This allows frontend development to proceed independently.

### Type Safety
All API responses are fully typed with TypeScript interfaces. This provides:
- Compile-time type checking
- IDE autocompletion
- Runtime type validation (where applicable)

### Error Recovery
The error handling system includes:
- Automatic token refresh
- User-friendly error messages
- Retry functionality for transient errors
- Graceful degradation when APIs are unavailable

## File Structure
```
src/services/
├── api.ts              # Main API service layer
├── API_DOCUMENTATION.md # This file
├── resumeService.ts    # Legacy resume service (re-exports)
└── index.ts           # Service exports

src/utils/
└── errors.ts          # Error handling utilities

src/hooks/
└── useApi.ts          # Custom React hooks for API
```

## Backend Integration Status

| Service | Status | Notes |
|---------|--------|-------|
| Auth | ✅ Fully implemented | Real JWT authentication |
| Resume | ✅ Fully implemented | Real file upload & processing |
| Resume Analysis | ✅ Fully implemented | AI-powered analysis |
| Interview | ⚠️ Placeholder | Mock data, backend endpoints pending |
| User Profile | ⚠️ Placeholder | Mock data, backend endpoints pending |
| System | ✅ Fully implemented | Real health checks |

## Testing

Run connectivity tests:
```bash
# From frontend directory
npm test -- --testPathPattern=api
```

Manual testing:
```javascript
// In browser console
import api from '@/services/api';
await api.system.getSystemHealth();
await api.auth.login({ email: 'test@example.com', password: 'password' });
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS_ORIGINS includes frontend URL
2. **Authentication Errors**: Check token storage and refresh flow
3. **Network Errors**: Verify backend is running on correct port
4. **Type Errors**: Update TypeScript interfaces if API response changes

### Debugging
- Check browser DevTools Network tab
- Examine localStorage for authentication tokens
- Use API testing tools (Postman, curl) to verify backend endpoints
- Review axios interceptor logs in console

## Contributing

When adding new API endpoints:
1. Add TypeScript interfaces in `api.ts`
2. Implement service methods in appropriate service class
3. Add JSDoc comments for documentation
4. Update this documentation file
5. Test with real backend or mock data