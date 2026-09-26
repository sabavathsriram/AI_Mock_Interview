import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { authService, setAuthTokens, clearAuthTokens, type UserResponse, type LoginRequest, type RegisterRequest } from '../services/api'

// Update User interface to match backend response
export interface User {
  id: string
  email: string
  full_name: string
  name: string // For compatibility with existing code
  role: string // Can be 'candidate' or 'admin' or other roles
  is_active: boolean
  created_at: string
  updated_at: string
  avatar?: string
}

export interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  setUser: (user: User | null) => void
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

  // Convert backend UserResponse to frontend User interface
  const transformUserResponse = (userResponse: UserResponse): User => {
    return {
      id: userResponse.id,
      email: userResponse.email,
      full_name: userResponse.full_name,
      name: userResponse.full_name, // For compatibility with existing code
      role: userResponse.role,
      is_active: userResponse.is_active,
      created_at: userResponse.created_at,
      updated_at: userResponse.updated_at,
    }
  }

  // Initialize auth state - check if user is authenticated
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (token) {
          // Try to get current user from API
          const response = await authService.getCurrentUser()
          if (response.data) {
            const transformedUser = transformUserResponse(response.data)
            setUser(transformedUser)
            localStorage.setItem('auth_user', JSON.stringify(transformedUser))
          } else {
            // Token might be invalid, clear it
            clearAuthTokens()
            localStorage.removeItem('auth_user')
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        clearAuthTokens()
        localStorage.removeItem('auth_user')
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const loginRequest: LoginRequest = { email, password }
      const response = await authService.login(loginRequest)
      
      if (response.data) {
        // Store tokens
        setAuthTokens(response.data)
        
        // Get user info
        const userResponse = await authService.getCurrentUser()
        if (userResponse.data) {
          const transformedUser = transformUserResponse(userResponse.data)
          setUser(transformedUser)
          localStorage.setItem('auth_user', JSON.stringify(transformedUser))
        }
      }
    } catch (error: any) {
      console.error('Login failed:', error)
      throw new Error(error.message || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    setIsLoading(true)
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
      throw new Error(error.message || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [login])

  const logout = useCallback(async () => {
    setIsLoading(true)
    try {
      // Call logout on the auth service
      await authService.logout()
      
      // Clear all auth data
      setUser(null)
      clearAuthTokens()
      localStorage.removeItem('auth_user')
    } catch (error) {
      console.error('Logout error:', error)
      // Still clear local data even if API call fails
      setUser(null)
      clearAuthTokens()
      localStorage.removeItem('auth_user')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refreshUser = useCallback(async () => {
    try {
      const response = await authService.getCurrentUser()
      if (response.data) {
        const transformedUser = transformUserResponse(response.data)
        setUser(transformedUser)
        localStorage.setItem('auth_user', JSON.stringify(transformedUser))
      }
    } catch (error) {
      console.error('Failed to refresh user:', error)
      // If we can't get user, assume token is invalid
      clearAuthTokens()
      localStorage.removeItem('auth_user')
      setUser(null)
    }
  }, [])

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
    setUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

AuthProvider.displayName = 'AuthProvider'
