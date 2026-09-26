import React, { useState } from 'react'
import { Dialog } from './Modal'
import { AlertTriangle } from 'lucide-react'

interface ConfirmDialogProps {
  title: string
  message: string
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void | Promise<void>
  confirmLabel?: string
  cancelLabel?: string
  isDangerous?: boolean
  isLoading?: boolean
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  title,
  message,
  isOpen,
  onClose,
  onConfirm,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDangerous = false,
  isLoading = false,
}) => {
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await Promise.resolve(onConfirm())
      onClose()
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      primaryAction={{
        label: confirmLabel,
        onClick: handleConfirm,
        loading: loading || isLoading,
      }}
      secondaryAction={{
        label: cancelLabel,
        onClick: onClose,
      }}
    >
      <div className="flex gap-3">
        {isDangerous && (
          <AlertTriangle className="w-5 h-5 text-warning-600 dark:text-warning-400 flex-shrink-0" />
        )}
        <p className="text-dark-600 dark:text-dark-400">{message}</p>
      </div>
    </Dialog>
  )
}

ConfirmDialog.displayName = 'ConfirmDialog'

/**
 * Hook for managing confirm dialog state
 */
export const useConfirmDialog = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [config, setConfig] = useState<Omit<ConfirmDialogProps, 'isOpen' | 'onClose'>>({
    title: '',
    message: '',
    onConfirm: () => {},
  })

  const open = (dialogConfig: Omit<ConfirmDialogProps, 'isOpen' | 'onClose' | 'onConfirm'> & { onConfirm: () => void | Promise<void> }) => {
    setConfig(dialogConfig)
    setIsOpen(true)
  }

  const close = () => {
    setIsOpen(false)
  }

  return {
    ...config,
    isOpen,
    onClose: close,
    open,
  }
}
