import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/utils/cn'

interface DropdownItem {
  label: string
  value: string
  icon?: React.ReactNode
  divider?: boolean
}

interface DropdownProps {
  items: DropdownItem[]
  trigger: React.ReactNode
  onSelect?: (value: string) => void
  align?: 'left' | 'right'
  className?: string
}

export const Dropdown: React.FC<DropdownProps> = ({
  items,
  trigger,
  onSelect,
  align = 'left',
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleSelect = (value: string) => {
    onSelect?.(value)
    setIsOpen(false)
  }

  return (
    <div ref={containerRef} className={cn('relative inline-block', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded"
      >
        {trigger}
      </button>

      {isOpen && (
        <div
          className={cn(
            'absolute z-50 min-w-[160px] rounded-lg shadow-lg bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700 py-1 mt-2 animate-slide-up',
            align === 'right' ? 'right-0' : 'left-0',
          )}
        >
          {items.map((item, index) => (
            <div key={index}>
              {item.divider ? (
                <div className="my-1 border-t border-dark-200 dark:border-dark-700" />
              ) : (
                <button
                  onClick={() => handleSelect(item.value)}
                  className={cn(
                    'w-full px-3 py-2 text-sm text-left flex items-center gap-2 hover:bg-dark-100 dark:hover:bg-dark-700 transition-colors',
                    'text-dark-900 dark:text-white',
                  )}
                >
                  {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
                  <span>{item.label}</span>
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

Dropdown.displayName = 'Dropdown'

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  helperText?: string
  options: Array<{ value: string; label: string }>
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, options, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-dark-900 dark:text-white mb-1.5">
            {label}
          </label>
        )}

        <select
          ref={ref}
          className={cn(
            'w-full px-3 py-2 text-sm rounded-md transition-all duration-200',
            'bg-white dark:bg-dark-800 border border-dark-300 dark:border-dark-600',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
            'text-dark-900 dark:text-white',
            error && 'border-error-500 focus-visible:ring-error-500',
            className,
          )}
          {...props}
        >
          <option value="">Select an option</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

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

Select.displayName = 'Select'
