import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { Send, Loader, AlertCircle, Clock, CheckCircle } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { useAuth } from '@/contexts/AuthContext'
import { interviewService } from '@/services/api'
import './InterviewQuestion.css'

interface InterviewState {
  session_id: string
  status: string
  current_question_index: number
  total_questions: number
  current_question: {
    question_id: string
    question_text: string
    question_type: string
    difficulty: string
    category: string
    key_points?: string[]
    tags?: string[]
  } | null
  started_at: string
}

export const InterviewQuestion: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()

  const [interviewState, setInterviewState] = useState<InterviewState | null>(null)
  const [answerText, setAnswerText] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [timeElapsed, setTimeElapsed] = useState(0)
  
  // Get first question from location state if available
  const firstQuestion = (location.state as any)?.firstQuestion

  // Load interview state on mount
  useEffect(() => {
    const loadInterview = async () => {
      if (!sessionId) {
        setError('Interview session ID not found')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const status = await interviewService.getInterviewStatus(sessionId)
        
        // CRITICAL: Check if interview is completed
        // Completed interviews should NOT be displayed in the active question interface
        if (status.status && status.status.toLowerCase() === 'completed') {
          console.log(`[DEBUG] Interview ${sessionId} is completed. Redirecting to results page.`)
          setLoading(false)
          navigate(`/interview/${sessionId}/results`)
          return
        }
        
        // Use first question from state if available, otherwise use a placeholder
        const currentQuestion = firstQuestion || {
          question_id: `q_${status.current_question_index}`,
          question_text: 'Loading question...',
          question_type: 'text',
          difficulty: 'medium',
          category: 'General'
        }
        
        setInterviewState({
          session_id: sessionId,
          status: status.status,
          current_question_index: status.current_question_index,
          total_questions: status.total_questions,
          current_question: currentQuestion,
          started_at: new Date().toISOString(),
        })
        setError(null)
      } catch (err: any) {
        setError(err.message || 'Failed to load interview')
      } finally {
        setLoading(false)
      }
    }

    loadInterview()
  }, [sessionId, firstQuestion, navigate])

  // Timer
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeElapsed((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleSubmitAnswer = async () => {
    if (!sessionId || !answerText.trim() || !interviewState?.current_question) {
      setError('Please provide an answer')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      // Submit answer
      await interviewService.submitAnswer(sessionId, {
        question_id: interviewState.current_question.question_id,
        answer: answerText,
      })

      // Get next question
      const nextResponse = await interviewService.getNextQuestion(sessionId)

      if (nextResponse.is_complete) {
        // Interview is complete, redirect to results
        navigate(`/interview/${sessionId}/results`)
      } else {
        // Move to next question
        setAnswerText('')
        setInterviewState((prev) =>
          prev
            ? {
                ...prev,
                current_question_index: nextResponse.current_question_index,
                current_question: nextResponse.current_question || null,
              }
            : null
        )
      }
    } catch (err: any) {
      setError(err.message || 'Failed to submit answer')
    } finally {
      setSubmitting(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Interview' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
            <div style={{ textAlign: 'center' }}>
              <Loader size={48} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 20px' }} />
              <p>Loading interview...</p>
            </div>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  if (!interviewState || !interviewState.current_question) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Interview' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <Card variant="default" padding="lg">
            <CardBody>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Error:</strong> {error || 'No question available'}
                </div>
              </div>
            </CardBody>
          </Card>
        </AppShellContent>
      </AppShell>
    )
  }

  const progress = ((interviewState.current_question_index) / interviewState.total_questions) * 100

  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Interview' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="interview-question-page">
          {/* Header with Progress */}
          <div className="interview-question-header">
            <div className="interview-question-progress">
              <span className="progress-label">Question {interviewState.current_question_index + 1} of {interviewState.total_questions}</span>
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
            <div className="interview-question-timer">
              <Clock size={16} />
              <span>{formatTime(timeElapsed)}</span>
            </div>
          </div>

          {error && (
            <Card variant="default" padding="md" className="error-card" style={{ marginBottom: '20px' }}>
              <CardBody>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <strong>Error:</strong> {error}
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Question Card */}
          <Card variant="elevated" padding="lg" className="question-card">
            <CardHeader>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '12px' }}>
                <Badge variant="primary" size="sm">{interviewState.current_question.category}</Badge>
                <Badge
                  variant={
                    interviewState.current_question.difficulty === 'easy'
                      ? 'success'
                      : interviewState.current_question.difficulty === 'hard'
                      ? 'error'
                      : 'warning'
                  }
                  size="sm"
                >
                  {interviewState.current_question.difficulty}
                </Badge>
              </div>
              <h2>{interviewState.current_question.question_text}</h2>
            </CardHeader>
            <CardBody>
              {interviewState.current_question.key_points && interviewState.current_question.key_points.length > 0 && (
                <div style={{ marginBottom: '24px' }}>
                  <p style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', color: 'var(--color-text-secondary)' }}>
                    Key points to cover:
                  </p>
                  <ul style={{ paddingLeft: '20px', fontSize: '14px' }}>
                    {interviewState.current_question.key_points.map((point, idx) => (
                      <li key={idx} style={{ marginBottom: '4px' }}>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardBody>
          </Card>

          {/* Answer Input */}
          <Card variant="default" padding="lg" className="answer-card">
            <CardHeader>
              <h3>Your Answer</h3>
            </CardHeader>
            <CardBody>
              <textarea
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="Type your answer here... Be thorough and explain your thinking."
                disabled={submitting}
                style={{
                  width: '100%',
                  minHeight: '200px',
                  padding: '12px',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '14px',
                  fontFamily: 'inherit',
                  resize: 'vertical',
                  color: 'var(--color-text-primary)',
                }}
              />
              <div style={{ marginTop: '16px', display: 'flex', gap: '12px', justifyContent: 'space-between' }}>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                  {answerText.length} characters
                </div>
                <Button
                  variant="primary"
                  size="lg"
                  icon={submitting ? <Loader size={18} /> : <Send size={18} />}
                  onClick={handleSubmitAnswer}
                  disabled={!answerText.trim() || submitting}
                >
                  {submitting ? 'Submitting...' : 'Submit Answer'}
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

InterviewQuestion.displayName = 'InterviewQuestion'
