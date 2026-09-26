import React from 'react'
import './Alert.css'
import { AlertCircle, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'

export type AlertType = 'success' | 'warning' | 'error' | 'info'

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: AlertType
  title?: string
  message: string
  onClose?: () => void
  dismissible?: boolean
}

/**
 * Alert Component
 * Displays informational messages with different severity levels
 */
export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  (
    {
      type = 'info',
      title,
      message,
      onClose,
      dismissible = true,
      className,
      ...props
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = React.useState(true)

    const handleClose = () => {
      setIsOpen(false)
      onClose?.()
    }

    if (!isOpen) return null

    const iconMap: Record<AlertType, React.ReactNode> = {
      success: <CheckCircle size={20} />,
      warning: <AlertTriangle size={20} />,
      error: <XCircle size={20} />,
      info: <AlertCircle size={20} />,
    }

    return (
      <div
        ref={ref}
        className={['alert', `alert-${type}`, className].filter(Boolean).join(' ')}
        role="alert"
        {...props}
      >
        <div className="alert-content">
          <span className="alert-icon">{iconMap[type]}</span>
          <div className="alert-text">
            {title && <div className="alert-title">{title}</div>}
            <div className="alert-message">{message}</div>
          </div>
        </div>
        {dismissible && (
          <button
            className="alert-close"
            onClick={handleClose}
            aria-label="Close alert"
          >
            ✕
          </button>
        )}
      </div>
    )
  }
)

Alert.displayName = 'Alert'
