import React from 'react'
import { cn } from '@/utils/cn'
import { colorVariants } from '@/utils/theme'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: keyof typeof colorVariants.input
  label?: string
  error?: string
  helperText?: string
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'default',
      label,
      error,
      helperText,
      icon,
      iconPosition = 'left',
      className,
      ...props
    },
    ref,
  ) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-dark-900 dark:text-white mb-1.5">
            {label}
          </label>
        )}

        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-dark-400 pointer-events-none">
              {icon}
            </div>
          )}

          <input
            ref={ref}
            className={cn(
              'w-full px-3 py-2 text-sm rounded-md transition-all duration-200',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
              'placeholder:text-dark-400 dark:placeholder:text-dark-500',
              colorVariants.input[variant],
              icon && iconPosition === 'left' ? 'pl-10' : '',
              icon && iconPosition === 'right' ? 'pr-10' : '',
              error && 'border-error-500 focus-visible:ring-error-500',
              className,
            )}
            {...props}
          />

          {icon && iconPosition === 'right' && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-400 pointer-events-none">
              {icon}
            </div>
          )}
        </div>

        {error && (
          <p className="mt-1.5 text-sm text-error-600 dark:text-error-400">{error}</p>
        )}

        {helperText && !error && (
          <p className="mt-1.5 text-sm text-dark-500 dark:text-dark-400">{helperText}</p>
        )}
      </div>
    )
  },
)

Input.displayName = 'Input'

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: keyof typeof colorVariants.input
  label?: string
  error?: string
  helperText?: string
  rows?: number
}

export const TextArea = React.forwardRef<HTMLTextAreaElement, TextAreaProps>(
  (
    {
      variant = 'default',
      label,
      error,
      helperText,
      rows = 4,
      className,
      ...props
    },
    ref,
  ) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-dark-900 dark:text-white mb-1.5">
            {label}
          </label>
        )}

        <textarea
          ref={ref}
          rows={rows}
          className={cn(
            'w-full px-3 py-2 text-sm rounded-md transition-all duration-200 resize-none',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
            'placeholder:text-dark-400 dark:placeholder:text-dark-500',
            colorVariants.input[variant],
            error && 'border-error-500 focus-visible:ring-error-500',
            className,
          )}
          {...props}
        />

        {error && (
          <p className="mt-1.5 text-sm text-error-600 dark:text-error-400">{error}</p>
        )}

        {helperText && !error && (
          <p className="mt-1.5 text-sm text-dark-500 dark:text-dark-400">{helperText}</p>
        )}
      </div>
    )
  },
)

TextArea.displayName = 'TextArea'
