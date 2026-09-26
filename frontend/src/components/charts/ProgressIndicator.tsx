import React from 'react'
import { cn } from '@/utils/cn'

interface ProgressIndicatorProps {
  value: number
  maxValue?: number
  label?: string
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'h-2',
  md: 'h-3',
  lg: 'h-4',
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  value,
  maxValue = 100,
  label,
  showLabel = true,
  size = 'md',
  className,
}) => {
  const percentage = (value / maxValue) * 100

  const getColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-success-500'
    if (percentage >= 60) return 'bg-primary-500'
    if (percentage >= 40) return 'bg-warning-500'
    return 'bg-error-500'
  }

  return (
    <div className={className}>
      {showLabel && label && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-dark-900 dark:text-white">{label}</span>
          <span className="text-sm font-semibold text-primary-600 dark:text-primary-400">
            {value}/{maxValue}
          </span>
        </div>
      )}

      <div className={cn('w-full bg-dark-200 dark:bg-dark-700 rounded-full overflow-hidden', sizeClasses[size])}>
        <div
          className={cn('h-full transition-all duration-500', getColor(percentage))}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  )
}

ProgressIndicator.displayName = 'ProgressIndicator'

interface CircularProgressProps {
  value: number
  maxValue?: number
  size?: number
  strokeWidth?: number
  label?: string
  className?: string
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value,
  maxValue = 100,
  size = 120,
  strokeWidth = 8,
  label,
  className,
}) => {
  const percentage = (value / maxValue) * 100
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percentage / 100) * circumference

  const getColor = (percentage: number) => {
    if (percentage >= 80) return '#22c55e'
    if (percentage >= 60) return '#5b8bff'
    if (percentage >= 40) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className={cn('flex flex-col items-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor(percentage)}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
        <text
          x={size / 2}
          y={size / 2}
          textAnchor="middle"
          dy="0.3em"
          className="text-2xl font-bold fill-dark-900 dark:fill-white"
        >
          {Math.round(percentage)}%
        </text>
      </svg>
      {label && <p className="mt-2 text-sm font-medium text-dark-600 dark:text-dark-400">{label}</p>}
    </div>
  )
}

CircularProgress.displayName = 'CircularProgress'
