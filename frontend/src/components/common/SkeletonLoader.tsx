import React from 'react'
import { cn } from '@/utils/cn'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number
  height?: string | number
  rounded?: 'sm' | 'md' | 'lg' | 'full'
  count?: number
  circle?: boolean
}

const roundedClasses = {
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  full: 'rounded-full',
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  rounded = 'md',
  count = 1,
  circle = false,
  className,
  ...props
}) => {
  const items = Array.from({ length: count })

  return (
    <div className="space-y-2">
      {items.map((_, index) => (
        <div
          key={index}
          style={{
            width: typeof width === 'number' ? `${width}px` : width,
            height: typeof height === 'number' ? `${height}px` : height,
          }}
          className={cn(
            'bg-dark-200 dark:bg-dark-700 animate-pulse',
            circle ? 'rounded-full' : roundedClasses[rounded],
            className,
          )}
          {...props}
        />
      ))}
    </div>
  )
}

Skeleton.displayName = 'Skeleton'

export const SkeletonCard: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="p-4 bg-white dark:bg-dark-800 rounded-lg border border-dark-200 dark:border-dark-700">
          <Skeleton height={20} width="60%" className="mb-3" />
          <Skeleton height={16} width="100%" count={2} />
          <Skeleton height={16} width="80%" className="mt-3" />
        </div>
      ))}
    </div>
  )
}

SkeletonCard.displayName = 'SkeletonCard'

export const SkeletonTableRow: React.FC<{ columns?: number }> = ({ columns = 4 }) => {
  return (
    <div className="flex gap-4">
      {Array.from({ length: columns }).map((_, index) => (
        <div key={index} className="flex-1">
          <Skeleton height={20} width="100%" />
        </div>
      ))}
    </div>
  )
}

SkeletonTableRow.displayName = 'SkeletonTableRow'

export const SkeletonAvatar: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  }

  return (
    <Skeleton
      circle
      width={sizeClasses[size].split(' ')[0].replace('w-', '')}
      height={sizeClasses[size].split(' ')[1].replace('h-', '')}
      className={sizeClasses[size]}
    />
  )
}

SkeletonAvatar.displayName = 'SkeletonAvatar'
