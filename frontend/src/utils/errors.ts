/**
 * Error handling utilities and types for API integration
 */

// Error types
export enum ErrorType {
  NETWORK = 'NETWORK',
  TIMEOUT = 'TIMEOUT',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION = 'VALIDATION',
  SERVER = 'SERVER',
  UNKNOWN = 'UNKNOWN'
}

export interface ApiError {
  type: ErrorType;
  message: string;
  status?: number;
  data?: any;
  originalError?: any;
}

// Error factory function
export function createApiError(
  type: ErrorType,
  message: string,
  status?: number,
  data?: any,
  originalError?: any
): ApiError {
  return {
    type,
    message,
    status,
    data,
    originalError
  };
}

// Determine error type from axios error
export function determineErrorType(error: any): ErrorType {
  if (!error.response) {
    // Network error or timeout
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return ErrorType.TIMEOUT;
    }
    return ErrorType.NETWORK;
  }

  const status = error.response.status;
  
  switch (status) {
    case 401:
      return ErrorType.UNAUTHORIZED;
    case 403:
      return ErrorType.FORBIDDEN;
    case 404:
      return ErrorType.NOT_FOUND;
    case 422:
    case 400:
      return ErrorType.VALIDATION;
    case 500:
    case 502:
    case 503:
    case 504:
      return ErrorType.SERVER;
    default:
      return ErrorType.UNKNOWN;
  }
}

// Format error message for display
export function formatErrorMessage(error: ApiError): string {
  switch (error.type) {
    case ErrorType.NETWORK:
      return 'Network error. Please check your connection and try again.';
    case ErrorType.TIMEOUT:
      return 'Request timed out. Please try again.';
    case ErrorType.UNAUTHORIZED:
      return 'Session expired. Please log in again.';
    case ErrorType.FORBIDDEN:
      return 'You do not have permission to perform this action.';
    case ErrorType.NOT_FOUND:
      return 'The requested resource was not found.';
    case ErrorType.VALIDATION:
      return error.message || 'Please check your input and try again.';
    case ErrorType.SERVER:
      return 'Server error. Please try again later.';
    default:
      return error.message || 'An unexpected error occurred.';
  }
}

// Check if error is retryable
export function isRetryableError(error: ApiError): boolean {
  return [
    ErrorType.NETWORK,
    ErrorType.TIMEOUT,
    ErrorType.SERVER
  ].includes(error.type);
}

// Extract validation errors from response
export function extractValidationErrors(data: any): Record<string, string[]> {
  if (!data || typeof data !== 'object') return {};
  
  if (data.errors && typeof data.errors === 'object') {
    return data.errors;
  }
  
  if (data.detail && Array.isArray(data.detail)) {
    const errors: Record<string, string[]> = {};
    data.detail.forEach((error: any) => {
      if (error.loc && error.msg) {
        const field = error.loc[error.loc.length - 1];
        if (!errors[field]) errors[field] = [];
        errors[field].push(error.msg);
      }
    });
    return errors;
  }
  
  return {};
}

// Create user-friendly error message from validation errors
export function formatValidationErrors(errors: Record<string, string[]>): string {
  const errorMessages = Object.entries(errors).map(([field, messages]) => {
    const fieldName = field.replace(/_/g, ' ');
    return `${fieldName}: ${messages.join(', ')}`;
  });
  
  return errorMessages.join('. ');
}

// Default error handler for API calls
export function handleApiError(error: any): ApiError {
  const type = determineErrorType(error);
  const message = error.message || 'An unexpected error occurred';
  const status = error.response?.status;
  const data = error.response?.data;
  
  return createApiError(type, message, status, data, error);
}