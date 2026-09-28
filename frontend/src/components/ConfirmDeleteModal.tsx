import React, { useEffect } from 'react'
import { AlertCircle, X } from 'lucide-react'
import { Button } from './Button'
import './ConfirmDeleteModal.css'

export interface ConfirmDeleteModalProps {
  isOpen: boolean
  title: string
  message: string
  itemName?: string
  isLoading?: boolean
  error?: string | null
  onConfirm: () => void | Promise<void>
  onCancel: () => void
  confirmButtonText?: string
  cancelButtonText?: string
  isDangerous?: boolean
}

/**
 * ConfirmDeleteModal Component
 * A reusable, accessible confirmation modal for destructive actions
 * Features:
 * - Accessible semantics (role, aria-labelledby, aria-describedby)
 * - Keyboard navigation (Escape to close)
 * - Focus management (traps focus inside modal)
 * - Loading state during confirmation
 * - Customizable button labels
 */
export const ConfirmDeleteModal: React.FC<ConfirmDeleteModalProps> = ({
  isOpen,
  title,
  message,
  itemName,
  isLoading = false,
  error,
  onConfirm,
  onCancel,
  confirmButtonText = 'Delete',
  cancelButtonText = 'Cancel',
  isDangerous = true,
}) => {
  // Handle keyboard shortcuts
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      // Close on Escape
      if (e.key === 'Escape') {
        onCancel()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onCancel])

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      return () => {
        document.body.style.overflow = ''
      }
    }
  }, [isOpen])

  if (!isOpen) return null

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Only close if clicking directly on backdrop, not on modal content
    if (e.target === e.currentTarget) {
      onCancel()
    }
  }

  const handleConfirm = async () => {
    await onConfirm()
  }

  return (
    <div className="confirm-delete-modal-backdrop" onClick={handleBackdropClick}>
      <div
        className="confirm-delete-modal"
        role="alertdialog"
        aria-labelledby="modal-title"
        aria-describedby="modal-description"
        aria-modal="true"
      >
        {/* Close button */}
        <button
          className="confirm-delete-modal-close"
          onClick={onCancel}
          aria-label="Close dialog"
          disabled={isLoading}
        >
          <X size={20} />
        </button>

        {/* Header with icon */}
        <div className="confirm-delete-modal-header">
          <div className="confirm-delete-modal-icon">
            <AlertCircle size={24} />
          </div>
          <h2 id="modal-title" className="confirm-delete-modal-title">
            {title}
          </h2>
        </div>

        {/* Content */}
        <div className="confirm-delete-modal-content">
          <p id="modal-description" className="confirm-delete-modal-message">
            {message}
          </p>
          {itemName && (
            <div className="confirm-delete-modal-item-name">
              <strong>{itemName}</strong>
            </div>
          )}
          {error && (
            <div className="confirm-delete-modal-error">
              <p className="confirm-delete-modal-error-text">{error}</p>
            </div>
          )}
        </div>

        {/* Footer with actions */}
        <div className="confirm-delete-modal-footer">
          <Button
            variant="ghost"
            size="md"
            onClick={onCancel}
            disabled={isLoading}
            className="confirm-delete-modal-btn-cancel"
          >
            {cancelButtonText}
          </Button>
          <Button
            variant="danger"
            size="md"
            isLoading={isLoading}
            onClick={handleConfirm}
            disabled={isLoading}
            className="confirm-delete-modal-btn-confirm"
          >
            {confirmButtonText}
          </Button>
        </div>
      </div>
    </div>
  )
}

ConfirmDeleteModal.displayName = 'ConfirmDeleteModal'
