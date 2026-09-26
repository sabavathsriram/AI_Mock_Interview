import React, { useState, useCallback } from 'react'
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastProps {
  id: string
  message: string
  type: ToastType
  duration?: number
}

interface ToastItemData {
  id: string
  message: string
  type: ToastType
  duration?: number
}

interface ToastContextType {
  toasts: ToastItemData[]
  addToast: (message: string, type?: ToastType, duration?: number) => void
  removeToast: (id: string) => void
}

export const ToastContext = React.createContext<ToastContextType | undefined>(undefined)

export const useToast = () => {
  const context = React.useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

export const Toast: React.FC<ToastProps & { onClose?: () => void }> = ({ message, type, onClose }) => {
  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle size={20} />,
    error: <AlertCircle size={20} />,
    warning: <AlertCircle size={20} />,
    info: <Info size={20} />,
  }
  const typeClasses: Record<ToastType, string> = {
    success: 'bg-success-50 text-success-900 border-success-200',
    error: 'bg-error-50 text-error-900 border-error-200',
    warning: 'bg-warning-50 text-warning-900 border-warning-200',
    info: 'bg-primary-50 text-primary-900 border-primary-200',
  }
  return (
    <div className={`flex items-center gap-3 p-4 rounded-lg border ${typeClasses[type]}`}>
      {icons[type]}
      <p className="flex-1 text-sm">{message}</p>
      {onClose && <button onClick={onClose}><X size={18} /></button>}
    </div>
  )
}

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItemData[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const addToast = useCallback((message: string, type: ToastType = 'info', duration = 3000) => {
    const id = Date.now().toString()
    const toast: ToastItemData = { id, message, type, duration }

    setToasts((prev) => [...prev, toast])

    if (duration) {
      setTimeout(() => removeToast(id), duration)
    }
  }, [removeToast])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

interface ToastContainerProps {
  toasts: ToastItemData[]
  onRemove: (id: string) => void
}

const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  )
}

interface ToastItemComponentProps {
  toast: ToastItemData
  onRemove: (id: string) => void
}

const ToastItem: React.FC<ToastItemComponentProps> = ({ toast, onRemove }) => {
  const typeClasses: Record<ToastType, string> = {
    success: 'bg-success-50 text-success-900 dark:bg-success-900 dark:text-success-100 border-success-200 dark:border-success-700',
    error: 'bg-error-50 text-error-900 dark:bg-error-900 dark:text-error-100 border-error-200 dark:border-error-700',
    warning: 'bg-warning-50 text-warning-900 dark:bg-warning-900 dark:text-warning-100 border-warning-200 dark:border-warning-700',
    info: 'bg-primary-50 text-primary-900 dark:bg-primary-900 dark:text-primary-100 border-primary-200 dark:border-primary-700',
  }

  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle size={20} />,
    error: <AlertCircle size={20} />,
    warning: <AlertCircle size={20} />,
    info: <Info size={20} />,
  }

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-lg border shadow-lg pointer-events-auto animate-slide-up ${typeClasses[toast.type]}`}
      role="alert"
    >
      <div className="flex-shrink-0 mt-0.5">{icons[toast.type]}</div>
      <p className="flex-1 text-sm font-medium">{toast.message}</p>
      <button
        onClick={() => onRemove(toast.id)}
        className="flex-shrink-0 text-current hover:opacity-70 transition-opacity"
        aria-label="Close"
      >
        <X size={18} />
      </button>
    </div>
  )
}