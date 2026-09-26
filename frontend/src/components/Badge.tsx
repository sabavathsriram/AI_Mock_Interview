import React from 'react'
import './Badge.css'

export type BadgeVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'neutral'
export type BadgeSize = 'sm' | 'md' | 'lg'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
  size?: BadgeSize
  icon?: React.ReactNode
  dot?: boolean
}

/**
 * Badge Component
 * A small label component for status, priority, or category indicators
 */
export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'primary', size = 'md', icon, dot = false, className, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={['badge', `badge-${variant}`, `badge-${size}`, dot && 'badge-dot', className]
          .filter(Boolean)
          .join(' ')}
        {...props}
      >
        {dot && <span className="badge-dot-indicator" />}
        {icon && <span className="badge-icon">{icon}</span>}
        {children && <span className="badge-text">{children}</span>}
      </span>
    )
  }
)

Badge.displayName = 'Badge'
