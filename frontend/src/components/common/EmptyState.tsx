import React from 'react'
import { cn } from '@/utils/cn'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className,
}) => {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12 px-4', className)}>
      {icon && (
        <div className="mb-4 text-dark-300 dark:text-dark-600">
          {typeof icon === 'string' ? (
            <span className="text-5xl">{icon}</span>
          ) : (
            <div className="w-16 h-16">{icon}</div>
          )}
        </div>
      )}

      <h3 className="text-lg font-semibold text-dark-900 dark:text-white mb-2">{title}</h3>

      {description && (
        <p className="text-dark-500 dark:text-dark-400 text-center max-w-sm mb-6">{description}</p>
      )}

      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-2 text-sm font-medium bg-primary-600 text-white hover:bg-primary-700 rounded-lg transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}

EmptyState.displayName = 'EmptyState'
