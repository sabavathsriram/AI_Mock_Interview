import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { authService, setAuthTokens, clearAuthTokens, type UserResponse, type LoginRequest, type RegisterRequest } from '../services/api'

// User interface matching backend UserResponse exactly
export interface User extends UserResponse {
  // Extend with any frontend-specific properties if needed
  // but primarily use backend contract
}

export interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Initialize auth state - check if user is authenticated
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setError(null)
        const token = localStorage.getItem('access_token')
        
        if (token) {
          // Try to get current user from API
          const response = await authService.getCurrentUser()
          if (response.data) {
            setUser(response.data as User)
          } else {
            // Token might be invalid, clear it
            clearAuthTokens()
            setUser(null)
          }
        } else {
          setUser(null)
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        clearAuthTokens()
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const loginRequest: LoginRequest = { email, password }
      const response = await authService.login(loginRequest)
      
      if (response.data) {
        // Store tokens
        setAuthTokens(response.data)
        
        // Get user info
        const userResponse = await authService.getCurrentUser()
        if (userResponse.data) {
          setUser(userResponse.data as User)
        }
      }
    } catch (error: any) {
      console.error('Login failed:', error)
      const errorMessage = error.message || 'Login failed. Please check your credentials.'
      setError(errorMessage)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const registerRequest: RegisterRequest = {
        email,
        full_name: fullName,
        password
      }
      
      const response = await authService.register(registerRequest)
      
      if (response.data) {
        // Auto-login after successful registration
        await login(email, password)
      }
    } catch (error: any) {
      console.error('Registration failed:', error)
      const errorMessage = error.message || 'Registration failed. Please try again.'
      setError(errorMessage)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [login])

  const logout = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      // Clear all auth data
      setUser(null)
      clearAuthTokens()
    } catch (error) {
      console.error('Logout error:', error)
      // Still clear local data even if something goes wrong
      setUser(null)
      clearAuthTokens()
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refreshUser = useCallback(async () => {
    try {
      const response = await authService.getCurrentUser()
      if (response.data) {
        setUser(response.data as User)
      }
    } catch (error) {
      console.error('Failed to refresh user:', error)
      // If we can't get user, assume token is invalid
      clearAuthTokens()
      setUser(null)
    }
  }, [])

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    error,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

AuthProvider.displayName = 'AuthProvider'
