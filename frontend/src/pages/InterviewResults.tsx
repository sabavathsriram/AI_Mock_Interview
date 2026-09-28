import React, { useState, useEffect, useRef } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Download,
  Share2,
  RefreshCw,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Target,
  BookOpen,
  Award,
  Loader,
} from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Progress } from '@/components/Progress'
import { interviewService, EvaluationResponse } from '@/services/api'
import './InterviewResults.css'

// Helper: Format IST timestamp (backend sends ISO UTC, display in IST)
const formatInterviewDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  const formatter = new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
  })
  const parts = formatter.formatToParts(date)
  let formatted = ''
  for (const part of parts) {
    if (part.type === 'literal' && part.value === ', ') {
      formatted += ', '
    } else if (part.type !== 'timeZoneName') {
      formatted += part.value
    }
  }
  return formatted + ' IST'
}

// Helper: Get performance rating (0-100% scale)
const getPerformanceRating = (percentage: number): string => {
  if (percentage >= 90) return 'Outstanding'
  if (percentage >= 75) return 'Excellent'
  if (percentage >= 65) return 'Good'
  if (percentage >= 50) return 'Satisfactory'
  return 'Needs Improvement'
}

// Helper: Get score variant for badge (0-100% scale)
const getScoreVariant = (percentage: number): 'success' | 'warning' | 'error' => {
  if (percentage >= 75) return 'success'
  if (percentage >= 60) return 'warning'
  return 'error'
}

export const InterviewResults: React.FC = () => {
  const { id } = useParams()
  const [evaluation, setEvaluation] = useState<EvaluationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [evaluatingInProgress, setEvaluatingInProgress] = useState(false)
  const evaluationTriggeredRef = useRef(false)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)
  
  useEffect(() => {
    const fetchAndTriggerEvaluation = async () => {
      if (!id) {
        setError('Interview ID not found')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        
        // First, try to get existing evaluations
        const eval_data = await interviewService.getEvaluation(id)
        
        // If no evaluations yet (overall_score is null), trigger evaluation
        if (eval_data.overall_score === null || eval_data.overall_score === undefined) {
          setEvaluatingInProgress(true)
          console.log(`[DEBUG] Overall score is ${eval_data.overall_score}, triggering evaluation`)
          
          try {
            // Trigger batch evaluation
            console.log(`[DEBUG] Calling triggerEvaluation for session ${id}`)
            const triggerResult = await interviewService.triggerEvaluation(id)
            console.log(`[DEBUG] Trigger evaluation response:`, triggerResult)
            
            // Wait a moment for evaluations to process, then fetch again
            await new Promise(resolve => setTimeout(resolve, 2000))
            
            console.log(`[DEBUG] Fetching updated evaluations`)
            const updated_eval = await interviewService.getEvaluation(id)
            console.log(`[DEBUG] Updated evaluation:`, updated_eval)
            setEvaluation(updated_eval)
          } catch (triggerErr) {
            console.error(`[DEBUG] Error during evaluation trigger:`, triggerErr)
            throw triggerErr
          } finally {
            setEvaluatingInProgress(false)
          }
        } else {
          setEvaluation(eval_data)
        }
        
        setError(null)
      } catch (err: any) {
        console.error('Failed to fetch evaluation:', err)
        setError(err.message || 'Failed to load evaluation results')
      } finally {
        setLoading(false)
      }
    }

    fetchAndTriggerEvaluation()
  }, [id])

  if (loading) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Interview History', href: '/interview-history' },
          { label: 'Results' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="results-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
            <Loader size={32} className="animate-spin" />
            <span style={{ marginLeft: '16px' }}>Loading evaluation results...</span>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  if (error || !evaluation) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Interview History', href: '/interview-history' },
          { label: 'Results' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="results-container">
            <Card variant="default" padding="lg">
              <CardBody>
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <AlertCircle size={48} style={{ color: 'var(--color-error-500)', marginBottom: '16px' }} />
                  <h2>Unable to Load Results</h2>
                  <p>{error || 'No evaluation data available'}</p>
                  <Link to="/interview-history">
                    <Button variant="primary" style={{ marginTop: '16px' }}>
                      Back to History
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

  const date = formatInterviewDateTime(evaluation.created_at)

  // Calculate percentage from 0-10 score
  const overallPercentage = evaluation.overall_score ? Math.round(evaluation.overall_score * 10) : 0
  const technicalPercentage = evaluation.technical_knowledge_score ? Math.round(evaluation.technical_knowledge_score * 10) : 0
  const communicationPercentage = evaluation.communication_score ? Math.round(evaluation.communication_score * 10) : 0
  const problemSolvingPercentage = evaluation.problem_solving_score ? Math.round(evaluation.problem_solving_score * 10) : 0

  // Use real evaluation data from backend
  const performanceByCategory = evaluation.categories && evaluation.categories.length > 0 
    ? evaluation.categories.map(cat => ({
        name: cat.name,
        score: cat.score ? Math.round(cat.score * 10) : 0,  // Convert 0-10 to 0-100
        feedback: cat.feedback
      }))
    : []

  const strengths = evaluation.strengths || []
  const improvements = evaluation.improvement_areas || []

  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Interview History', href: '/interview-history' },
        { label: 'Results' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="results-container">
          {/* Header Navigation */}
          <div className="results-nav">
            <Link to="/interview-history" className="results-back-link">
              <ArrowLeft size={18} />
              Back to History
            </Link>
            <div className="results-actions">
              <Button variant="ghost" size="sm" icon={<Download size={18} />} title="Download results as PDF" />
              <Button variant="ghost" size="sm" icon={<Share2 size={18} />} title="Share results" />
            </div>
          </div>

          {/* Main Header */}
          <div className="results-header">
            <div className="results-header-text">
              <h1>Interview Complete!</h1>
              <p>Interview • {date}</p>
            </div>
            <Link to="/interview/setup">
              <Button variant="primary" icon={<RefreshCw size={18} />}>
                Practice Again
              </Button>
            </Link>
          </div>

          {/* Overall Score Card */}
          {evaluation.overall_score === null || evaluation.overall_score === undefined ? (
            <Card variant="elevated" padding="lg" className="results-score-card">
              <CardBody>
                <div style={{ textAlign: 'center', padding: '32px' }}>
                  <Lightbulb size={48} style={{ color: 'var(--color-warning-500)', marginBottom: '16px' }} />
                  <h2>Evaluations Pending</h2>
                  <p style={{ color: '#666', marginTop: '8px', marginBottom: '16px' }}>
                    Your responses are being evaluated. Please check back in a few moments.
                  </p>
                  <p style={{ color: '#999', fontSize: '12px' }}>
                    Interview completed at {date}
                  </p>
                </div>
              </CardBody>
            </Card>
          ) : (
            <Card variant="elevated" padding="lg" className="results-score-card">
            <CardBody>
              <div className="results-score-inner">
                <div className="results-score-circle">
                  <svg viewBox="0 0 200 200">
                    <defs>
                      <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="var(--color-primary-600)" />
                        <stop offset="100%" stopColor="var(--color-secondary-600)" />
                      </linearGradient>
                    </defs>
                    <circle cx="100" cy="100" r="90" className="results-circle-bg" />
                    <circle
                      cx="100"
                      cy="100"
                      r="90"
                      className="results-circle-progress"
                      style={{
                        strokeDasharray: `${565.5 * (overallPercentage / 100)} 565.5`,
                      }}
                    />
                  </svg>
                  <div className="results-score-text">
                    <span className="results-score-value">{overallPercentage}%</span>
                    <span className="results-score-label">Overall Score</span>
                  </div>
                </div>
                <div className="results-score-details">
                  <div className="results-score-item">
                    <span>Performance</span>
                    <Badge variant={getScoreVariant(overallPercentage)}>
                      {getPerformanceRating(overallPercentage)}
                    </Badge>
                  </div>
                  <div className="results-score-item">
                    <span>Technical Knowledge</span>
                    <span className="results-score-item-value">{technicalPercentage}%</span>
                  </div>
                  <div className="results-score-item">
                    <span>Communication</span>
                    <span className="results-score-item-value">{communicationPercentage}%</span>
                  </div>
                  <div className="results-score-item">
                    <span>Problem Solving</span>
                    <span className="results-score-item-value">{problemSolvingPercentage}%</span>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
          )}

          {/* Two Column Layout - Only show if evaluations are available */}
          {evaluation.overall_score !== null && evaluation.overall_score !== undefined && (
          <div className="results-grid">
            {/* Left Column */}
            <div className="results-left">
              {/* Performance by Category */}
              <Card variant="default" padding="lg">
                <CardHeader>
                  <div className="results-card-header">
                    <TrendingUp size={20} />
                    <h2>Performance by Category</h2>
                  </div>
                </CardHeader>
                <CardBody>
                  <div className="results-performance-list">
                    {evaluation.categories.map((cat, idx) => {
                      const catPercentage = cat.score ? Math.round(cat.score * 10) : 0
                      return (
                        <div key={idx} className="results-performance-item">
                          <div className="results-performance-header">
                            <span className="results-performance-name">{cat.name}</span>
                            <Badge variant={getScoreVariant(catPercentage)} size="sm">{catPercentage}%</Badge>
                          </div>
                          <Progress value={catPercentage} color={getScoreVariant(catPercentage)} showPercent={false} />
                          <p className="results-performance-feedback">{cat.feedback}</p>
                        </div>
                      )
                    })}
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Right Column */}
            <div className="results-right">
              {/* Strengths */}
              <Card variant="default" padding="lg">
                <CardHeader>
                  <div className="results-card-header success">
                    <CheckCircle size={20} />
                    <h2>Your Strengths</h2>
                  </div>
                </CardHeader>
                <CardBody>
                  <ul className="results-insights-list">
                    {evaluation.strengths.map((strength, idx) => (
                      <li key={idx}>
                        <CheckCircle size={14} />
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </CardBody>
              </Card>

              {/* Areas for Improvement */}
              <Card variant="default" padding="lg">
                <CardHeader>
                  <div className="results-card-header warning">
                    <AlertCircle size={20} />
                    <h2>Areas to Improve</h2>
                  </div>
                </CardHeader>
                <CardBody>
                  <ul className="results-insights-list improvements">
                    {evaluation.improvement_areas.map((improvement, idx) => (
                      <li key={idx}>
                        <AlertCircle size={14} />
                        <span>{improvement}</span>
                      </li>
                    ))}
                  </ul>
                </CardBody>
              </Card>

              {/* Feedback */}
              <Card variant="default" padding="lg">
                <CardHeader>
                  <div className="results-card-header">
                    <Lightbulb size={20} />
                    <h2>Overall Feedback</h2>
                  </div>
                </CardHeader>
                <CardBody>
                  <p className="results-performance-feedback">{evaluation.overall_feedback}</p>
                </CardBody>
              </Card>
            </div>
          </div>
          )}

          {/* Bottom CTA */}
          <Card variant="elevated" padding="lg" className="results-footer-card">
            <CardBody>
              <div className="results-footer">
                <div className="results-footer-icon">
                  <Award size={32} />
                </div>
                <div className="results-footer-content">
                  <h3>Ready for Your Next Challenge?</h3>
                  <p>Review your evaluation, check out your skill assessment, and start your learning path to improve.</p>
                </div>
                <div className="results-footer-actions">
                  <Link to={`/skills?interview=${id}`}>
                    <Button variant="secondary" icon={<TrendingUp size={18} />}>
                      View Skills
                    </Button>
                  </Link>
                  <Link to={`/learning?interview=${id}`}>
                    <Button variant="primary" icon={<BookOpen size={18} />}>
                      Learning Path
                    </Button>
                  </Link>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

InterviewResults.displayName = 'InterviewResults'
