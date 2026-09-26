/**
 * Comprehensive API Service Layer for AI Mock Interview System
 * 
 * This file provides a complete TypeScript API client for all backend endpoints.
 * It includes authentication, resumes, interviews, users, and system endpoints.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosProgressEvent } from 'axios';
import { handleApiError, ErrorType, formatErrorMessage } from '@/utils/errors';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default configuration
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await authService.refreshToken(refreshToken);
          const tokens = response.data;
          if (tokens.access_token) {
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);
            originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    // Handle other errors using our error utilities
    const apiError = handleApiError(error);
    const userFriendlyMessage = formatErrorMessage(apiError);
    
    return Promise.reject({
      ...apiError,
      message: userFriendlyMessage,
    });
  }
);

// Type Definitions
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

// API Service Base Class
abstract class BaseService {
  protected api: AxiosInstance;

  constructor() {
    this.api = api;
  }

  protected async request<T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<T> = await this.api.request(config);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error: any) {
      throw error;
    }
  }

  protected async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  protected async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  protected async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  protected async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PATCH', url, data });
  }

  protected async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }
}

// Authentication Service
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

/**
 * Authentication service for user login, registration, and token management
 */
class AuthService extends BaseService {
  /**
   * Authenticate user with email and password
   * @param credentials - Login credentials
   * @returns JWT tokens and user information
   */
  async login(credentials: LoginRequest): Promise<ApiResponse<TokenResponse>> {
    return this.post<TokenResponse>('/auth/login', credentials);
  }

  /**
   * Register a new user account
   * @param userData - User registration data
   * @returns Created user information
   */
  async register(userData: RegisterRequest): Promise<ApiResponse<UserResponse>> {
    return this.post<UserResponse>('/auth/register', userData);
  }

  /**
   * Refresh access token using refresh token
   * @param refreshToken - Refresh token from previous authentication
   * @returns New JWT tokens
   */
  async refreshToken(refreshToken: string): Promise<ApiResponse<TokenResponse>> {
    return this.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken });
  }

  /**
   * Get current authenticated user information
   * @returns Current user details
   */
  async getCurrentUser(): Promise<ApiResponse<UserResponse>> {
    return this.get<UserResponse>('/auth/me');
  }

  /**
   * Change current user's password
   * @param data - Password change request
   * @returns Success message
   */
  async changePassword(data: ChangePasswordRequest): Promise<ApiResponse<{ message: string }>> {
    return this.post<{ message: string }>('/auth/change-password', data);
  }

  /**
   * Logout user and clear authentication data
   */
  async logout(): Promise<void> {
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  /**
   * Check if user is currently authenticated
   * @returns True if user has valid authentication tokens
   */
  async isAuthenticated(): Promise<boolean> {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      await this.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }
}

// Resume Service (existing but enhanced)
export interface ResumeUploadResponse {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  display_name: string;
  is_primary: boolean;
  extracted_text: string;
  extraction_metadata: Record<string, unknown>;
  uploaded_at: string;
}

export interface ResumeDetailResponse {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  mime_type: string;
  display_name: string;
  is_primary: boolean;
  extraction_status: string;
  extraction_error?: string;
  extraction_metadata: Record<string, unknown>;
  uploaded_at: string;
  last_accessed_at?: string;
}

export interface ResumeListResponse {
  resumes: ResumeDetailResponse[];
  total_count: number;
}

export interface FileSupportInfo {
  supported_formats: string[];
  unsupported_formats: string[];
  max_file_size_mb: number;
  max_file_size_bytes: number;
}

/**
 * Resume management service for uploading, listing, and processing resumes
 */
class ResumeService extends BaseService {
  /**
   * Upload and process a resume document
   * @param file - Resume file to upload
   * @param displayName - Optional display name for the resume
   * @param isPrimary - Whether this should be set as primary resume
   * @param onProgress - Callback for upload progress updates
   * @returns Upload response with extracted text and metadata
   */
  async uploadResume(
    file: File,
    displayName?: string,
    isPrimary: boolean = false,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<ApiResponse<ResumeUploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);
    if (displayName) {
      formData.append('display_name', displayName);
    }
    formData.append('is_primary', isPrimary.toString());

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (progressEvent.total) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress?.({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      },
    };

    return this.post<ResumeUploadResponse>('/resumes/upload', formData, config);
  }

  async listResumes(): Promise<ApiResponse<ResumeListResponse>> {
    return this.get<ResumeListResponse>('/resumes/list');
  }

  async getResume(resumeId: string): Promise<ApiResponse<ResumeDetailResponse>> {
    return this.get<ResumeDetailResponse>(`/resumes/${resumeId}`);
  }

  async deleteResume(resumeId: string): Promise<ApiResponse<{ success: boolean; message: string }>> {
    return this.delete<{ success: boolean; message: string }>(`/resumes/${resumeId}`);
  }

  async getResumeText(resumeId: string): Promise<ApiResponse<{
    resume_id: string;
    filename: string;
    file_type: string;
    extracted_text: string;
    extraction_metadata: Record<string, unknown>;
  }>> {
    return this.get(`/resumes/text/${resumeId}`);
  }

  async getSupportedFormats(): Promise<ApiResponse<FileSupportInfo>> {
    return this.get<FileSupportInfo>('/resumes/info/supported-formats');
  }

  async validateFile(file: File): Promise<{ valid: boolean; error?: string }> {
    const formatsInfo = await this.getSupportedFormats();
    const fileExtension = ('.' + file.name.split('.').pop()?.toLowerCase()).toLowerCase();

    if (!formatsInfo.data.supported_formats.includes(fileExtension)) {
      if (formatsInfo.data.unsupported_formats.includes(fileExtension)) {
        return {
          valid: false,
          error: `File type ${fileExtension} is not supported for resume upload`,
        };
      }
      return {
        valid: false,
        error: `File type ${fileExtension} is not recognized`,
      };
    }

    if (file.size > formatsInfo.data.max_file_size_bytes) {
      const maxMb = formatsInfo.data.max_file_size_mb;
      return {
        valid: false,
        error: `File size exceeds maximum allowed size of ${maxMb.toFixed(1)} MB`,
      };
    }

    if (file.size === 0) {
      return {
        valid: false,
        error: 'File is empty',
      };
    }

    return { valid: true };
  }

  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  static getFileTypeLabel(fileType: string): string {
    const labels: Record<string, string> = {
      pdf: 'PDF Document',
      docx: 'Word Document (DOCX)',
      doc: 'Word Document (DOC)',
      txt: 'Text File',
      rtf: 'Rich Text Format',
      odt: 'OpenDocument Text',
      html: 'HTML Document',
      markdown: 'Markdown Document',
    };

    return labels[fileType.toLowerCase()] || fileType.toUpperCase();
  }
}

// Resume Intelligence/Analysis Service
export interface ResumeAnalysisRequest {
  resume_id: string;
  force_reanalyze?: boolean;
}

export interface ResumeAnalysisResponse {
  resume_id: string;
  user_id: string;
  analysis: any;
  status: string;
  analyzed_at: string;
  message?: string;
}

export interface ResumeAnalysisSummary {
  resume_id: string;
  candidate_name?: string;
  experience_level?: string;
  primary_domains: string[];
  secondary_domains: string[];
  total_skills: number;
  total_experience_entries: number;
  total_projects: number;
  overall_confidence?: number;
  resume_strengths: string[];
  skill_gaps: string[];
  important_technologies: string[];
  analyzed_at: string;
}

class ResumeAnalysisService extends BaseService {
  async analyzeResume(request: ResumeAnalysisRequest): Promise<ApiResponse<ResumeAnalysisResponse>> {
    return this.post<ResumeAnalysisResponse>('/resumes/analysis/analyze', request);
  }

  async getAnalysisResults(resumeId: string): Promise<ApiResponse<ResumeAnalysisResponse>> {
    return this.get<ResumeAnalysisResponse>(`/resumes/analysis/results/${resumeId}`);
  }

  async getAnalysisStatus(resumeId: string): Promise<ApiResponse<{
    resume_id: string;
    analysis_status: string;
    analyzed_at: string;
    analysis_version?: string;
    has_analysis: boolean;
    error?: string;
  }>> {
    return this.get(`/resumes/analysis/status/${resumeId}`);
  }

  async getAnalysisSummary(resumeId: string): Promise<ApiResponse<ResumeAnalysisSummary>> {
    return this.get<ResumeAnalysisSummary>(`/resumes/analysis/summary/${resumeId}`);
  }
}

// Interview Service (placeholder implementations for now)
export interface InterviewTemplate {
  id: string;
  name: string;
  description: string;
  duration_minutes: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  question_count: number;
  skills: string[];
  is_active: boolean;
}

export interface InterviewSession {
  id: string;
  user_id: string;
  resume_id?: string;
  template_id?: string;
  title: string;
  status: 'pending' | 'active' | 'completed' | 'cancelled';
  current_question_index: number;
  total_questions: number;
  start_time?: string;
  end_time?: string;
  created_at: string;
  updated_at: string;
}

export interface InterviewQuestion {
  id: string;
  interview_id: string;
  question_index: number;
  question_text: string;
  question_type: 'technical' | 'behavioral' | 'system_design';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  skills: string[];
  time_limit_seconds?: number;
  is_answered: boolean;
}

export interface InterviewAnswer {
  question_id: string;
  answer_text: string;
  answer_audio_url?: string;
  time_taken_seconds: number;
  confidence_score?: number;
}

export interface InterviewEvaluation {
  interview_id: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
  feedback_text: string;
  evaluated_at: string;
}

class InterviewService extends BaseService {
  // Placeholder methods - will be implemented when backend endpoints are available
  async getInterviewTemplates(): Promise<ApiResponse<InterviewTemplate[]>> {
    // For now, return mock data
    const mockTemplates: InterviewTemplate[] = [
      {
        id: '1',
        name: 'Frontend Developer',
        description: 'Assess frontend development skills including React, TypeScript, and CSS',
        duration_minutes: 45,
        difficulty: 'intermediate',
        question_count: 10,
        skills: ['React', 'TypeScript', 'CSS', 'JavaScript'],
        is_active: true,
      },
      {
        id: '2',
        name: 'Backend Developer',
        description: 'Assess backend development skills including Python, FastAPI, and databases',
        duration_minutes: 60,
        difficulty: 'intermediate',
        question_count: 12,
        skills: ['Python', 'FastAPI', 'MongoDB', 'REST API'],
        is_active: true,
      },
    ];
    
    return Promise.resolve({
      data: mockTemplates,
      status: 200,
    });
  }

  async startInterview(data: {
    template_id?: string;
    resume_id?: string;
    title?: string;
    custom_settings?: any;
  }): Promise<ApiResponse<InterviewSession>> {
    // For now, return mock session
    const mockSession: InterviewSession = {
      id: `session_${Date.now()}`,
      user_id: 'current_user',
      template_id: data.template_id || '1',
      resume_id: data.resume_id,
      title: data.title || 'Mock Interview',
      status: 'active',
      current_question_index: 0,
      total_questions: 10,
      start_time: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return Promise.resolve({
      data: mockSession,
      status: 201,
    });
  }

  async getInterviewSession(sessionId: string): Promise<ApiResponse<InterviewSession>> {
    // For now, return mock session
    const mockSession: InterviewSession = {
      id: sessionId,
      user_id: 'current_user',
      title: 'Mock Interview Session',
      status: 'active',
      current_question_index: 3,
      total_questions: 10,
      created_at: new Date(Date.now() - 3600000).toISOString(),
      updated_at: new Date().toISOString(),
    };

    return Promise.resolve({
      data: mockSession,
      status: 200,
    });
  }

  async getNextQuestion(sessionId: string): Promise<ApiResponse<InterviewQuestion>> {
    // For now, return mock question
    const mockQuestion: InterviewQuestion = {
      id: `question_${Date.now()}`,
      interview_id: sessionId,
      question_index: 4,
      question_text: 'Explain the difference between useState and useEffect in React.',
      question_type: 'technical',
      difficulty: 'intermediate',
      skills: ['React', 'Hooks'],
      time_limit_seconds: 120,
      is_answered: false,
    };

    return Promise.resolve({
      data: mockQuestion,
      status: 200,
    });
  }

  async submitAnswer(sessionId: string, questionId: string, answer: InterviewAnswer): Promise<ApiResponse<{
    success: boolean;
    next_question_available: boolean;
    evaluation?: any;
  }>> {
    // For now, return mock response
    return Promise.resolve({
      data: {
        success: true,
        next_question_available: true,
      },
      status: 200,
    });
  }

  async completeInterview(sessionId: string): Promise<ApiResponse<InterviewEvaluation>> {
    // For now, return mock evaluation
    const mockEvaluation: InterviewEvaluation = {
      interview_id: sessionId,
      overall_score: 85,
      technical_score: 90,
      communication_score: 80,
      problem_solving_score: 85,
      strengths: ['Strong technical knowledge', 'Good problem-solving approach'],
      areas_for_improvement: ['Could improve communication clarity', 'Needs more real-world examples'],
      recommendations: ['Practice explaining concepts out loud', 'Study system design patterns'],
      feedback_text: 'Great performance overall. You demonstrated strong technical knowledge but could work on explaining your thought process more clearly.',
      evaluated_at: new Date().toISOString(),
    };

    return Promise.resolve({
      data: mockEvaluation,
      status: 200,
    });
  }

  async getInterviewHistory(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<ApiResponse<PaginatedResponse<InterviewSession>>> {
    // For now, return mock history
    const mockSessions: InterviewSession[] = [
      {
        id: 'session_1',
        user_id: 'current_user',
        title: 'Frontend Technical Interview',
        status: 'completed',
        current_question_index: 10,
        total_questions: 10,
        start_time: new Date(Date.now() - 86400000).toISOString(),
        end_time: new Date(Date.now() - 86340000).toISOString(),
        created_at: new Date(Date.now() - 86500000).toISOString(),
        updated_at: new Date(Date.now() - 86340000).toISOString(),
      },
    ];

    return Promise.resolve({
      data: {
        items: mockSessions,
        total: 1,
        page: params?.page || 1,
        page_size: params?.page_size || 10,
        total_pages: 1,
      },
      status: 200,
    });
  }

  async getInterviewEvaluation(sessionId: string): Promise<ApiResponse<InterviewEvaluation>> {
    // For now, return mock evaluation
    const mockEvaluation: InterviewEvaluation = {
      interview_id: sessionId,
      overall_score: 85,
      technical_score: 90,
      communication_score: 80,
      problem_solving_score: 85,
      strengths: ['Strong technical knowledge', 'Good problem-solving approach'],
      areas_for_improvement: ['Could improve communication clarity', 'Needs more real-world examples'],
      recommendations: ['Practice explaining concepts out loud', 'Study system design patterns'],
      feedback_text: 'Great performance overall. You demonstrated strong technical knowledge but could work on explaining your thought process more clearly.',
      evaluated_at: new Date().toISOString(),
    };

    return Promise.resolve({
      data: mockEvaluation,
      status: 200,
    });
  }
}

// User Service (for profile and settings)
export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  bio?: string;
  job_title?: string;
  company?: string;
  location?: string;
  website?: string;
  github?: string;
  linkedin?: string;
  skills: string[];
  experience_years: number;
  preferred_interview_types: string[];
  notification_settings: {
    email_notifications: boolean;
    push_notifications: boolean;
    interview_reminders: boolean;
    weekly_digest: boolean;
  };
  created_at: string;
  updated_at: string;
}

export interface UserStats {
  total_interviews: number;
  completed_interviews: number;
  average_score: number;
  best_score: number;
  total_learning_hours: number;
  skills_mastered: number;
  skills_in_progress: number;
}

class UserService extends BaseService {
  // Placeholder methods - will be implemented when backend endpoints are available
  async getUserProfile(): Promise<ApiResponse<UserProfile>> {
    // For now, return mock profile
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    const mockProfile: UserProfile = {
      id: user.id || 'current_user',
      email: user.email || 'user@example.com',
      full_name: user.full_name || 'John Doe',
      bio: 'Passionate software developer with 5+ years of experience in web development.',
      job_title: 'Senior Frontend Developer',
      company: 'Tech Corp Inc.',
      location: 'San Francisco, CA',
      website: 'https://johndoe.dev',
      github: 'johndoe',
      linkedin: 'johndoe',
      skills: ['React', 'TypeScript', 'Python', 'FastAPI', 'MongoDB'],
      experience_years: 5,
      preferred_interview_types: ['technical', 'behavioral', 'system_design'],
      notification_settings: {
        email_notifications: true,
        push_notifications: true,
        interview_reminders: true,
        weekly_digest: false,
      },
      created_at: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date().toISOString(),
    };

    return Promise.resolve({
      data: mockProfile,
      status: 200,
    });
  }

  async updateUserProfile(profile: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    // For now, return updated mock profile
    const currentProfile = await this.getUserProfile();
    const updatedProfile = { ...currentProfile.data, ...profile, updated_at: new Date().toISOString() };
    
    return Promise.resolve({
      data: updatedProfile,
      status: 200,
    });
  }

  async getUserStats(): Promise<ApiResponse<UserStats>> {
    // For now, return mock stats
    const mockStats: UserStats = {
      total_interviews: 12,
      completed_interviews: 10,
      average_score: 78,
      best_score: 95,
      total_learning_hours: 45,
      skills_mastered: 8,
      skills_in_progress: 4,
    };

    return Promise.resolve({
      data: mockStats,
      status: 200,
    });
  }

  async updateNotificationSettings(settings: Partial<UserProfile['notification_settings']>): Promise<ApiResponse<UserProfile>> {
    const currentProfile = await this.getUserProfile();
    const updatedSettings = { ...currentProfile.data.notification_settings, ...settings };
    const updatedProfile = { 
      ...currentProfile.data, 
      notification_settings: updatedSettings,
      updated_at: new Date().toISOString()
    };
    
    return Promise.resolve({
      data: updatedProfile,
      status: 200,
    });
  }
}

// System Service (health checks, etc.)
export interface SystemHealth {
  status: string;
  database: string;
  database_status: string;
  timestamp: string;
}

export interface LLMHealth {
  status: string;
  model: string;
  available: boolean;
  response_time_ms?: number;
}

class SystemService extends BaseService {
  private getRootUrl(): string {
    // Remove /api/v1 from the base URL for root endpoints
    const baseUrl = API_BASE_URL;
    return baseUrl.replace(/\/api\/v1$/, '');
  }

  async getSystemHealth(): Promise<ApiResponse<SystemHealth>> {
    // Root endpoint, not under /api/v1
    const rootUrl = this.getRootUrl();
    return axios.get<SystemHealth>(`${rootUrl}/health`).then(response => ({
      data: response.data,
      status: response.status,
    }));
  }

  async getDatabaseStatus(): Promise<ApiResponse<{ status: string; message: string }>> {
    // Root endpoint, not under /api/v1
    const rootUrl = this.getRootUrl();
    return axios.get<{ status: string; message: string }>(`${rootUrl}/database/test`).then(response => ({
      data: response.data,
      status: response.status,
    }));
  }

  async getLLMHealth(): Promise<ApiResponse<LLMHealth>> {
    // This is under /api/v1
    return this.get<LLMHealth>('/llm/health');
  }
}

// Export all services as singleton instances
export const authService = new AuthService();
export const resumeService = new ResumeService();
export const resumeAnalysisService = new ResumeAnalysisService();
export const interviewService = new InterviewService();
export const userService = new UserService();
export const systemService = new SystemService();

// Helper function to set auth tokens
export const setAuthTokens = (tokens: TokenResponse) => {
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
};

// Helper function to clear auth tokens
export const clearAuthTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

// Export API instance for direct use if needed
export { api };

// Default export for convenience
export default {
  auth: authService,
  resumes: resumeService,
  analysis: resumeAnalysisService,
  interviews: interviewService,
  users: userService,
  system: systemService,
  api,
  setAuthTokens,
  clearAuthTokens,
};