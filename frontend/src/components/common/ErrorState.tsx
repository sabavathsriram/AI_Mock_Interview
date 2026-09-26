import React from 'react'
import { AlertTriangle } from 'lucide-react'
import { cn } from '@/utils/cn'

interface ErrorStateProps {
  title?: string
  message: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
  showIcon?: boolean
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  action,
  className,
  showIcon = true,
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 bg-error-50 dark:bg-error-900/20 rounded-lg border border-error-200 dark:border-error-700',
        className,
      )}
    >
      {showIcon && (
        <AlertTriangle className="w-12 h-12 text-error-600 dark:text-error-400 mb-4" />
      )}

      <h3 className="text-lg font-semibold text-error-900 dark:text-error-100 mb-2">{title}</h3>

      <p className="text-error-800 dark:text-error-200 text-center max-w-sm mb-6">{message}</p>

      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-2 text-sm font-medium bg-error-600 text-white hover:bg-error-700 rounded-lg transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

ErrorState.displayName = 'ErrorState'

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <ErrorState message="An unexpected error occurred. Please refresh the page." />
        )
      )
    }

    return this.props.children
  }
}
