import React from 'react'
import './Progress.css'

export interface ProgressProps {
  value: number
  max?: number
  label?: string
  showPercent?: boolean
  color?: 'primary' | 'success' | 'warning' | 'error'
}

/**
 * Progress Component
 * Linear progress bar with optional label and percentage display
 */
export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  label,
  showPercent = false,
  color = 'primary',
}) => {
  const percentage = Math.min(Math.round((value / max) * 100), 100)

  return (
    <div className="progress-wrapper">
      {(label || showPercent) && (
        <div className="progress-header">
          {label && <span className="progress-label">{label}</span>}
          {showPercent && <span className="progress-percent">{percentage}%</span>}
        </div>
      )}
      <div className={['progress', `progress-${color}`].filter(Boolean).join(' ')}>
        <div className="progress-bar" style={{ width: `${percentage}%` }} />
      </div>
    </div>
  )
}

Progress.displayName = 'Progress'
