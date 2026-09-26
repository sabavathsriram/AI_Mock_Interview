import React from 'react'
import { cn } from '@/utils/cn'
import { colorVariants } from '@/utils/theme'

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: keyof typeof colorVariants.badge
  size?: 'sm' | 'md' | 'lg'
  icon?: React.ReactNode
  dismissible?: boolean
  onDismiss?: () => void
}

const sizeClasses = {
  sm: 'px-2 py-1 text-xs rounded-sm',
  md: 'px-2.5 py-1 text-sm rounded-md',
  lg: 'px-3 py-1.5 text-base rounded-md',
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      icon,
      dismissible = false,
      onDismiss,
      className,
      children,
      ...props
    },
    ref,
  ) => {
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center gap-1.5 font-medium',
          colorVariants.badge[variant],
          sizeClasses[size],
          className,
        )}
        {...props}
      >
        {icon && icon}
        {children}
        {dismissible && (
          <button
            onClick={onDismiss}
            className="ml-1 hover:opacity-70 transition-opacity"
            aria-label="Dismiss"
          >
            <svg
              className="w-3 h-3"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </span>
    )
  },
)

Badge.displayName = 'Badge'
