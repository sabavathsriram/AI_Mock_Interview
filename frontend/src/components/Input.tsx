import React from 'react'
import './Input.css'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  icon?: React.ReactNode
}

/**
 * Input Component
 * A flexible text input with optional label, error, and helper text
 */
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, icon, className, ...props }, ref) => {
    const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`

    return (
      <div className="input-wrapper">
        {label && (
          <label htmlFor={inputId} className="input-label">
            {label}
            {props.required && <span className="input-required">*</span>}
          </label>
        )}
        <div className={['input-container', error && 'input-error'].filter(Boolean).join(' ')}>
          {icon && <span className="input-icon">{icon}</span>}
          <input
            ref={ref}
            id={inputId}
            className={['input', icon && 'input-with-icon', className]
              .filter(Boolean)
              .join(' ')}
            {...props}
          />
        </div>
        {error && <div className="input-error-text">{error}</div>}
        {helperText && !error && <div className="input-helper-text">{helperText}</div>}
      </div>
    )
  }
)

Input.displayName = 'Input'

/* ============================================================================
   SELECT COMPONENT
   ============================================================================ */

export interface SelectOption {
  value: string
  label: string
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  helperText?: string
  options: SelectOption[]
  placeholder?: string
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, options, placeholder, className, ...props }, ref) => {
    const selectId = props.id || `select-${Math.random().toString(36).substr(2, 9)}`

    return (
      <div className="input-wrapper">
        {label && (
          <label htmlFor={selectId} className="input-label">
            {label}
            {props.required && <span className="input-required">*</span>}
          </label>
        )}
        <div className={['input-container', error && 'input-error'].filter(Boolean).join(' ')}>
          <select
            ref={ref}
            id={selectId}
            className={['input', 'select', className].filter(Boolean).join(' ')}
            {...props}
          >
            {placeholder && <option value="">{placeholder}</option>}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        {error && <div className="input-error-text">{error}</div>}
        {helperText && !error && <div className="input-helper-text">{helperText}</div>}
      </div>
    )
  }
)

Select.displayName = 'Select'

/* ============================================================================
   TEXTAREA COMPONENT
   ============================================================================ */

export interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  helperText?: string
  charLimit?: number
}

export const TextArea = React.forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ label, error, helperText, charLimit, className, value, onChange, ...props }, ref) => {
    const textareaId = props.id || `textarea-${Math.random().toString(36).substr(2, 9)}`
    const charCount = typeof value === 'string' ? value.length : 0

    return (
      <div className="input-wrapper">
        {label && (
          <label htmlFor={textareaId} className="input-label">
            {label}
            {props.required && <span className="input-required">*</span>}
          </label>
        )}
        <div className={['input-container', error && 'input-error'].filter(Boolean).join(' ')}>
          <textarea
            ref={ref}
            id={textareaId}
            className={['input', 'textarea', className].filter(Boolean).join(' ')}
            value={value}
            onChange={onChange}
            maxLength={charLimit}
            {...props}
          />
        </div>
        <div className="input-footer">
          {charLimit && (
            <span className="input-char-count">
              {charCount} / {charLimit}
            </span>
          )}
          {error && <div className="input-error-text">{error}</div>}
          {helperText && !error && <div className="input-helper-text">{helperText}</div>}
        </div>
      </div>
    )
  }
)

TextArea.displayName = 'TextArea'
