import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, Eye, MoreVertical, Trash2 } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import { Alert } from '@/components/Alert'
import { ConfirmDeleteModal } from '@/components/ConfirmDeleteModal'
import { interviewService } from '@/services/api'
import './InterviewHistory.css'

interface InterviewHistoryItem {
  session_id: string
  interview_type: string
  target_position: string
  target_company?: string
  difficulty: string
  total_questions: number
  questions_answered: number
  interview_status: string
  started_at?: string
  completed_at?: string
}

export const InterviewHistory: React.FC = () => {
  const navigate = useNavigate()
  const [interviews, setInterviews] = useState<InterviewHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [selectedInterview, setSelectedInterview] = useState<InterviewHistoryItem | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  useEffect(() => {
    fetchInterviewHistory()
  }, [])

  const fetchInterviewHistory = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await interviewService.getInterviewHistory()
      setInterviews(data.interviews || [])
    } catch (err: any) {
      setError(err.message || 'Failed to load interview history')
      console.error('Error fetching interview history:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  const formatInterviewType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')
  }

  const formatDifficulty = (difficulty: string) => {
    return difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
  }

  // Format status from enum to readable label
  const formatStatus = (status: string): string => {
    const statusMap: Record<string, string> = {
      'in_progress': 'In Progress',
      'evaluation_pending': 'Evaluation Pending',
      'completed': 'Completed',
      'failed': 'Evaluation Failed',
      'not_started': 'Not Started',
      'paused': 'Paused',
      'cancelled': 'Cancelled',
    }
    return statusMap[status] || formatInterviewType(status)
  }

  // Get action buttons based on status
  const getActionLabel = (status: string): string => {
    const statusLower = status.toLowerCase()
    switch (statusLower) {
      case 'in_progress':
        return 'Resume'
      case 'evaluation_pending':
        return 'View Status'
      case 'completed':
        return 'View Results'
      case 'failed':
        return 'Retry Evaluation'
      default:
        return 'View'
    }
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'badge-success'
      case 'in_progress':
        return 'badge-warning'
      case 'not_started':
        return 'badge-info'
      case 'paused':
        return 'badge-warning'
      case 'cancelled':
        return 'badge-danger'
      default:
        return 'badge-default'
    }
  }

  const handleViewInterview = (interview: InterviewHistoryItem) => {
    // For completed interviews, navigate to results page
    // For active/in-progress interviews, navigate to question page
    if (interview.interview_status && interview.interview_status.toLowerCase() === 'completed') {
      navigate(`/interview/${interview.session_id}/results`)
    } else {
      navigate(`/interview/${interview.session_id}/question`)
    }
  }

  const handleDeleteClick = (interview: InterviewHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation()
    setSelectedInterview(interview)
    setDeleteModalOpen(true)
    setDeleteError(null)
  }

  const handleConfirmDelete = async () => {
    if (!selectedInterview) return

    try {
      setIsDeleting(true)
      setDeleteError(null)

      await interviewService.deleteInterview(selectedInterview.session_id)

      // Remove from UI immediately
      setInterviews((prevInterviews) =>
        prevInterviews.filter((i) => i.session_id !== selectedInterview.session_id)
      )

      setDeleteModalOpen(false)
      setSelectedInterview(null)

      // Show success message
      const interviewTitle = `${selectedInterview.target_position} - ${formatDate(selectedInterview.started_at)}`
      setSuccessMessage(`Interview "${interviewTitle}" has been deleted successfully.`)

      // Auto-dismiss success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage(null)
      }, 5000)
    } catch (err: any) {
      setDeleteError(err.message || 'Failed to delete interview. Please try again.')
      console.error('Error deleting interview:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleCancelDelete = () => {
    setDeleteModalOpen(false)
    setSelectedInterview(null)
    setDeleteError(null)
  }

  if (loading) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Interview History' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="interview-history-page">
            <div className="interview-history-header">
              <div className="interview-history-header-content">
                <h1>Interview History</h1>
                <p>Review your past interview performance</p>
              </div>
            </div>
            <Card variant="default" padding="lg">
              <CardBody>
                <div className="loading-state">
                  <p>Loading your interviews...</p>
                </div>
              </CardBody>
            </Card>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  if (error) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Interview History' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="interview-history-page">
            <div className="interview-history-header">
              <div className="interview-history-header-content">
                <h1>Interview History</h1>
                <p>Review your past interview performance</p>
              </div>
            </div>
            <Card variant="default" padding="lg">
              <CardBody>
                <div className="error-state">
                  <AlertCircle size={48} />
                  <h3>Error Loading History</h3>
                  <p>{error}</p>
                  <Button variant="primary" size="sm" onClick={fetchInterviewHistory}>
                    Retry
                  </Button>
                </div>
              </CardBody>
            </Card>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  if (interviews.length === 0) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Interview History' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="interview-history-page">
            <div className="interview-history-header">
              <div className="interview-history-header-content">
                <h1>Interview History</h1>
                <p>Review your past interview performance</p>
              </div>
            </div>

            <Card variant="default" padding="lg" className="interview-history-empty">
              <CardBody>
                <div className="interview-history-empty-content">
                  <AlertCircle size={48} />
                  <h3>No interviews yet</h3>
                  <p>You haven't completed any interviews yet.</p>
                  <p className="interview-history-empty-subtext">
                    Start your first mock interview to build your skills!
                  </p>
                  <Link to="/dashboard">
                    <Button variant="primary" size="sm">
                      Start an Interview
                    </Button>
                  </Link>
                </div>
              </CardBody>
            </Card>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Interview History' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="interview-history-page">
          {/* Header */}
          <div className="interview-history-header">
            <div className="interview-history-header-content">
              <h1>Interview History</h1>
              <p>Review your past interview performance</p>
            </div>
          </div>

          {/* Success Message */}
          {successMessage && (
            <Alert
              type="success"
              message={successMessage}
              dismissible
              onClose={() => setSuccessMessage(null)}
            />
          )}

          {/* Interviews List */}
          <div className="interviews-list">
            {interviews.map((interview) => (
              <Card
                key={interview.session_id}
                variant="default"
                padding="lg"
                className="interview-history-card"
              >
                <CardBody>
                  <div className="interview-history-item">
                    <div className="interview-history-item-header">
                      <div className="interview-history-item-title">
                        <h3>{formatInterviewType(interview.interview_type)}</h3>
                        <span className={`status-badge ${getStatusBadgeClass(interview.interview_status)}`}>
                          {formatStatus(interview.interview_status)}
                        </span>
                      </div>
                      <div className="interview-history-item-actions">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewInterview(interview)}
                          className="view-button"
                        >
                          <Eye size={16} />
                          {getActionLabel(interview.interview_status)}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => handleDeleteClick(interview, e)}
                          className="delete-button"
                          title="Delete interview"
                          disabled={isDeleting}
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </div>

                    <div className="interview-history-item-details">
                      <div className="detail-row">
                        <span className="detail-label">Position:</span>
                        <span className="detail-value">{interview.target_position}</span>
                      </div>
                      {interview.target_company && (
                        <div className="detail-row">
                          <span className="detail-label">Company:</span>
                          <span className="detail-value">{interview.target_company}</span>
                        </div>
                      )}
                      <div className="detail-row">
                        <span className="detail-label">Date:</span>
                        <span className="detail-value">{formatDate(interview.started_at)}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Difficulty:</span>
                        <span className="detail-value">{formatDifficulty(interview.difficulty)}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Progress:</span>
                        <span className="detail-value">
                          {interview.questions_answered} / {interview.total_questions} questions answered
                        </span>
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>

          {/* Delete Confirmation Modal */}
          <ConfirmDeleteModal
            isOpen={deleteModalOpen}
            title="Delete Interview?"
            message="Are you sure you want to delete this interview? This will permanently remove the interview, answers, evaluation, and results from your history."
            itemName={selectedInterview ? `${selectedInterview.target_position} - ${formatDate(selectedInterview.started_at)}` : undefined}
            isLoading={isDeleting}
            error={deleteError}
            onConfirm={handleConfirmDelete}
            onCancel={handleCancelDelete}
            confirmButtonText="Delete Interview"
            cancelButtonText="Cancel"
          />
        </div>
      </AppShellContent>
    </AppShell>
  )
}

InterviewHistory.displayName = 'InterviewHistory'