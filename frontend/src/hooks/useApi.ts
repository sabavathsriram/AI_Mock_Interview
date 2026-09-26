/**
 * Custom hooks for consistent API data fetching with loading and error states
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { ApiError } from '@/utils/errors';

// Hook return type
export interface UseApiResult<T> {
  data: T | null;
  isLoading: boolean;
  error: ApiError | null;
  fetchData: () => Promise<void>;
  reset: () => void;
}

// Configuration options
export interface UseApiOptions<T> {
  initialData?: T | null;
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError) => void;
}

/**
 * Hook for fetching data from an API endpoint
 */
export function useApi<T>(
  fetchFn: () => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiResult<T> {
  const {
    initialData = null,
    immediate = true,
    onSuccess,
    onError
  } = options;

  const [data, setData] = useState<T | null>(initialData);
  const [isLoading, setIsLoading] = useState(immediate);
  const [error, setError] = useState<ApiError | null>(null);
  const isMounted = useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetchFn();
      
      if (isMounted.current) {
        setData(result);
        setError(null);
        onSuccess?.(result);
      }
    } catch (err: any) {
      if (isMounted.current) {
        setError(err);
        setData(null);
        onError?.(err);
      }
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
      }
    }
  }, [fetchFn, onSuccess, onError]);

  // Fetch data immediately if requested
  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [fetchData, immediate]);

  const reset = useCallback(() => {
    setData(initialData);
    setError(null);
    setIsLoading(false);
  }, [initialData]);

  return {
    data,
    isLoading,
    error,
    fetchData,
    reset
  };
}

/**
 * Hook for API mutations (POST, PUT, DELETE)
 */
export interface UseApiMutationResult<T, R> {
  data: R | null;
  isLoading: boolean;
  error: ApiError | null;
  mutate: (data: T) => Promise<R | null>;
  reset: () => void;
}

export function useApiMutation<T, R>(
  mutationFn: (data: T) => Promise<R>,
  options: {
    onSuccess?: (data: R) => void;
    onError?: (error: ApiError) => void;
  } = {}
): UseApiMutationResult<T, R> {
  const { onSuccess, onError } = options;
  const [data, setData] = useState<R | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const isMounted = useRef(true);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  const mutate = useCallback(async (mutationData: T): Promise<R | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await mutationFn(mutationData);
      
      if (isMounted.current) {
        setData(result);
        setError(null);
        onSuccess?.(result);
        return result;
      }
    } catch (err: any) {
      if (isMounted.current) {
        setError(err);
        onError?.(err);
      }
      throw err;
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
      }
    }

    return null;
  }, [mutationFn, onSuccess, onError]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    mutate,
    reset
  };
}

/**
 * Hook for handling loading states with debouncing
 */
export function useLoadingState(initialState = false, delay = 300) {
  const [isLoading, setIsLoading] = useState(initialState);
  const [showLoader, setShowLoader] = useState(initialState);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
    
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (loading) {
      // Show loader immediately
      setShowLoader(true);
    } else {
      // Hide loader after delay (to prevent flash)
      timeoutRef.current = setTimeout(() => {
        setShowLoader(false);
      }, delay);
    }
  }, [delay]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return { isLoading, showLoader, setLoading };
}