/**
 * Comprehensive API Service Layer for AI Mock Interview System
 * 
 * This file provides a complete TypeScript API client for all backend endpoints.
 * It includes authentication, resumes, interviews, users, and system endpoints.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosProgressEvent } from 'axios';
import { handleApiError, ErrorType, formatErrorMessage } from '@/utils/errors';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Create axios instance with default configuration
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token and handle FormData
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // For FormData, remove Content-Type so axios sets it with proper boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
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
    // Skip refresh if this IS the refresh endpoint to avoid infinite loop
    if (error.response?.status === 401 && 
        !originalRequest._retry && 
        !originalRequest.url?.includes('/auth/refresh')) {
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
        
        // Only redirect if not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    // If it's a 401 on the refresh endpoint itself, clear tokens and redirect
    if (error.response?.status === 401 && originalRequest.url?.includes('/auth/refresh')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      if (!window.location.pathname.includes('/login')) {
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
  extracted_text?: string;
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

// Resume Intelligence Types
export interface ContactInfo {
  email?: string | null;
  phone?: string | null;
  location?: string | null;
}

export interface EducationEntry {
  degree?: string | null;
  field_of_study?: string | null;
  institution?: string | null;
  graduation_year?: number | null;
  cgpa?: number | null;
  percentage?: number | null;
}

export interface SkillsCategory {
  programming_languages: string[];
  frameworks: string[];
  libraries: string[];
  databases: string[];
  cloud_devops: string[];
  ai_ml: string[];
  other: string[];
}

export interface ProjectEntry {
  name?: string | null;
  description?: string | null;
  technologies: string[];
  link?: string | null;
}

export interface WorkExperienceEntry {
  company?: string | null;
  position?: string | null;
  duration?: string | null;
  start_year?: number | null;
  end_year?: number | null;
  description?: string | null;
  key_achievements: string[];
}

export interface InternshipEntry {
  company?: string | null;
  position?: string | null;
  duration?: string | null;
  start_month_year?: string | null;
  end_month_year?: string | null;
  description?: string | null;
  technologies: string[];
}

export interface CertificationEntry {
  name?: string | null;
  issuer?: string | null;
  issue_date?: string | null;
  expiry_date?: string | null;
  link?: string | null;
}

export interface AchievementEntry {
  title?: string | null;
  description?: string | null;
  date?: string | null;
}

export interface CandidateProfile {
  resume_id: string;
  user_id: string;
  candidate_name?: string | null;
  contact: ContactInfo;
  education: EducationEntry[];
  skills: SkillsCategory;
  projects: ProjectEntry[];
  experience: WorkExperienceEntry[];
  internships: InternshipEntry[];
  certifications: CertificationEntry[];
  achievements: AchievementEntry[];
  additional_information: string[];
}

export interface ResumeIntelligenceResponse {
  resume_id: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  profile?: CandidateProfile;
  error?: string;
  llm_model_used?: string;
  analyzed_at?: string;
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

    // Do NOT manually set Content-Type header for multipart/form-data
    // Axios automatically handles the boundary when FormData is passed
    const config: AxiosRequestConfig = {
      // Remove headers or set them without Content-Type
      // The Authorization header will be added by the request interceptor
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

  async analyzeResume(resumeId: string): Promise<ApiResponse<ResumeIntelligenceResponse>> {
    return this.post<ResumeIntelligenceResponse>(`/resumes/${resumeId}/analyze`, {});
  }

  async getResumeIntelligence(resumeId: string): Promise<ApiResponse<ResumeIntelligenceResponse>> {
    return this.get<ResumeIntelligenceResponse>(`/resumes/${resumeId}/intelligence`);
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

// Interview Service
export interface StartInterviewRequest {
  resume_id: string
  interview_type: string
  target_position: string
  target_company?: string
  difficulty: string
  duration_minutes: number
  num_questions: number
}

export interface QuestionResponse {
  question_id: string
  question_text: string
  question_type: string
  difficulty: string
  category: string
  key_points?: string[]
  tags?: string[]
}

export interface StartInterviewResponse {
  session_id: string
  status: string
  current_question_index: number
  total_questions: number
  current_question: QuestionResponse
  started_at: string
}

export interface SubmitAnswerRequest {
  question_id: string
  answer: string
}

export interface SubmitAnswerResponse {
  response_id: string
  status: string
}

export interface InterviewStatusResponse {
  interview_session_id: string
  status: string
  current_question_index: number
  total_questions: number
  completed_questions: string[]
  overall_score?: number
  time_spent_seconds?: number
}

export interface CompleteInterviewResponse {
  interview_session_id: string
  status: string
  overall_score?: number
  evaluation_id?: string
  skill_assessment_id?: string
  recommendation_ids: string[]
  message: string
}

export interface EvaluationResponse {
  _id: string
  interview_session_id: string
  user_id: string
  overall_score: number
  overall_feedback: string
  categories: Array<{
    name: string
    weight: number
    score: number
    feedback: string
  }>
  strengths: string[]
  weaknesses: string[]
  improvement_areas: string[]
  technical_knowledge_score: number
  communication_score: number
  problem_solving_score: number
  skill_gaps: string[]
  training_recommendations: string[]
  is_ai_generated: boolean
  ai_model_used: string
  confidence_score: number
  created_at: string
  updated_at: string
}

export interface SkillMetricResponse {
  skill_name: string
  category: string
  current_proficiency: number
  confidence_score: number
  evidence: string[]
  last_assessed_date: string
  assessment_method: string
  previous_proficiency?: number
  proficiency_change?: number
  trend: string
}

export interface SkillAssessmentResponse {
  _id: string
  user_id: string
  interview_session_id: string
  assessment_title: string
  assessment_date: string
  assessment_type: string
  skills: SkillMetricResponse[]
  average_proficiency: number
  strongest_skills: string[]
  weakest_skills: string[]
  categories: Record<string, number>
  is_ai_assessed: boolean
  ai_model_used: string
  ai_confidence: number
  recommended_skill_focus: string[]
  skill_gap_analysis: string[]
  is_comprehensive: boolean
  created_at: string
  updated_at: string
}

export interface LearningResourceResponse {
  title: string
  type: string
  url: string
  duration: string
  estimated_time_hours?: number
  difficulty: string
  rating?: number
  source: string
  description?: string
}

export interface LearningPathResponse {
  name: string
  description: string
  target_skill: string
  total_estimated_time_hours: number
  resources: LearningResourceResponse[]
  order: number[]
}

export interface LearningRecommendationResponse {
  _id: string
  user_id: string
  interview_session_id: string
  skill_assessment_id?: string
  evaluation_id?: string
  title: string
  description: string
  priority_level: number
  target_skills: string[]
  skill_gaps_addressed: string[]
  resources: LearningResourceResponse[]
  learning_paths: LearningPathResponse[]
  estimated_completion_time_hours: number
  recommended_start_date: string
  recommended_completion_date: string
  is_ai_generated: boolean
  ai_model_used: string
  confidence_score: number
  created_at: string
  updated_at: string
}

// Generate Questions Interfaces
export interface GenerateQuestionsRequest {
  resume_id: string
  interview_type: string
  difficulty_level: string
  target_position: string
  target_company?: string
  num_questions?: number
  job_description_id?: string
}

export interface QuestionItemResponse {
  id: string
  question_text: string
  question_type: string
  difficulty: string
  category: string
  key_points?: string[]
  tags?: string[]
  is_ai_generated: boolean
  ai_model_used?: string
}

export interface GenerateQuestionsResponse {
  success: boolean
  questions: QuestionItemResponse[]
  message: string
}

export interface GetQuestionsResponse {
  interview_session_id: string
  questions: QuestionItemResponse[]
  total_count: number
}

class InterviewService extends BaseService {
  async startInterview(request: StartInterviewRequest): Promise<StartInterviewResponse> {
    try {
      const response = await this.post<StartInterviewResponse>('/interviews/start', request)
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to start interview')
    }
  }

  async submitAnswer(
    sessionId: string,
    request: SubmitAnswerRequest
  ): Promise<SubmitAnswerResponse> {
    try {
      const response = await this.post<SubmitAnswerResponse>(
        `/interviews/${sessionId}/responses`,
        request
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to submit answer')
    }
  }

  async getNextQuestion(sessionId: string): Promise<any> {
    try {
      const response = await this.post<any>(
        `/interviews/${sessionId}/next-question`,
        {}
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to get next question')
    }
  }

  async getInterviewStatus(sessionId: string): Promise<InterviewStatusResponse> {
    try {
      const response = await this.get<InterviewStatusResponse>(
        `/interviews/${sessionId}`
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch interview status')
    }
  }

  async completeInterview(sessionId: string): Promise<CompleteInterviewResponse> {
    try {
      const response = await this.post<CompleteInterviewResponse>(
        `/interviews/${sessionId}/complete`
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to complete interview')
    }
  }

  async abandonInterview(sessionId: string): Promise<CompleteInterviewResponse> {
    try {
      const response = await this.post<CompleteInterviewResponse>(
        `/interviews/${sessionId}/abandon`
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to abandon interview')
    }
  }

  async getEvaluation(interviewSessionId: string): Promise<EvaluationResponse> {
    try {
      const response = await this.get<EvaluationResponse>(
        `/interviews/${interviewSessionId}/evaluation`
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch evaluation')
    }
  }

  async getSkillAssessment(interviewSessionId: string): Promise<SkillAssessmentResponse> {
    try {
      const response = await this.get<SkillAssessmentResponse>(
        `/interviews/${interviewSessionId}/skills`
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch skill assessment')
    }
  }

  async getRecommendations(interviewSessionId: string): Promise<LearningRecommendationResponse[]> {
    try {
      const response = await this.get<LearningRecommendationResponse[]>(
        `/interviews/${interviewSessionId}/recommendations`
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch recommendations')
    }
  }

  async generateQuestions(request: GenerateQuestionsRequest): Promise<GenerateQuestionsResponse> {
    try {
      const response = await this.post<GenerateQuestionsResponse>(
        '/interviews/generate-questions',
        request
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to generate interview questions')
    }
  }

  async getInterviewQuestions(interviewSessionId: string): Promise<GetQuestionsResponse> {
    try {
      const response = await this.get<GetQuestionsResponse>(
        `/interviews/${interviewSessionId}/questions`
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch interview questions')
    }
  }

  async getInterviewHistory(): Promise<any> {
    try {
      const response = await this.get<any>('/interviews')
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch interview history')
    }
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
    // Backend endpoint not yet implemented
    throw new Error('User profile endpoint is not yet implemented on the backend');
  }

  async updateUserProfile(profile: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    // Backend endpoint not yet implemented
    throw new Error('User profile update endpoint is not yet implemented on the backend');
  }

  async getUserStats(): Promise<ApiResponse<UserStats>> {
    // Backend endpoint not yet implemented
    throw new Error('User stats endpoint is not yet implemented on the backend');
  }

  async updateNotificationSettings(settings: Partial<UserProfile['notification_settings']>): Promise<ApiResponse<UserProfile>> {
    // Backend endpoint not yet implemented
    throw new Error('Notification settings update endpoint is not yet implemented on the backend');
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