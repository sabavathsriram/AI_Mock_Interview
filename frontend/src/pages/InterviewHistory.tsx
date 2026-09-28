import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, Eye } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
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

  const handleViewInterview = (sessionId: string) => {
    navigate(`/interview/${sessionId}/summary`)
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
                          {formatInterviewType(interview.interview_status)}
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewInterview(interview.session_id)}
                        className="view-button"
                      >
                        <Eye size={16} />
                        View
                      </Button>
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
        </div>
      </AppShellContent>
    </AppShell>
  )
}

InterviewHistory.displayName = 'InterviewHistory'