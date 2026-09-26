import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Skeleton, SkeletonCard } from './SkeletonLoader'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: 'candidate' | 'admin'
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white dark:bg-dark-900 p-4">
        <SkeletonCard count={3} />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

ProtectedRoute.displayName = 'ProtectedRoute'

interface PublicRouteProps {
  children: React.ReactNode
}

export const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white dark:bg-dark-900 p-4">
        <SkeletonCard count={3} />
      </div>
    )
  }

  // Redirect to dashboard if already authenticated
  if (isAuthenticated && (location.pathname === '/login' || location.pathname === '/register')) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

PublicRoute.displayName = 'PublicRoute'
