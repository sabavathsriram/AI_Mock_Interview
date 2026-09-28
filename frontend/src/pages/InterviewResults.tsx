import React, { useState, useEffect } from 'react'
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

export const InterviewResults: React.FC = () => {
  const { id } = useParams()
  const [evaluation, setEvaluation] = useState<EvaluationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const fetchEvaluation = async () => {
      if (!id) {
        setError('Interview ID not found')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const eval_data = await interviewService.getEvaluation(id)
        setEvaluation(eval_data)
        setError(null)
      } catch (err: any) {
        console.error('Failed to fetch evaluation:', err)
        setError(err.message || 'Failed to load evaluation results')
      } finally {
        setLoading(false)
      }
    }

    fetchEvaluation()
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

  const date = new Date(evaluation.created_at).toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })

  const getScoreVariant = (score: number): 'success' | 'warning' | 'error' => {
    if (score >= 75) return 'success'
    if (score >= 60) return 'warning'
    return 'error'
  }

  const getPerformanceRating = (score: number): string => {
    if (score >= 85) return 'Outstanding'
    if (score >= 75) return 'Excellent'
    if (score >= 65) return 'Good'
    if (score >= 50) return 'Satisfactory'
    return 'Needs Improvement'
  }

  const performanceByCategory = [
    { name: 'Technical Knowledge', score: 85, feedback: 'Excellent understanding of core concepts' },
    { name: 'Communication', score: 72, feedback: 'Could improve articulation of complex ideas' },
    { name: 'Problem Solving', score: 89, feedback: 'Strong analytical approach demonstrated' },
    { name: 'Code Quality', score: 65, feedback: 'Focus on optimization and best practices' },
    { name: 'System Design', score: 52, feedback: 'This is your weakest area - needs practice' },
  ]

  const questions = [
    { num: 1, question: 'Stack vs Queue Data Structures', score: 85, status: 'excellent' },
    { num: 2, question: 'HTTP Request Process', score: 72, status: 'good' },
    { num: 3, question: 'Quick Sort Complexity', score: 89, status: 'excellent' },
    { num: 4, question: 'URL Shortener System Design', score: 52, status: 'needs-improvement' },
  ]

  const strengths = [
    'Clear explanation of fundamental concepts',
    'Logical problem-solving approach',
    'Good use of examples',
  ]

  const improvements = [
    'Practice system design questions - your weakest area',
    'Work on deep diving into trade-offs and scalability',
    'Improve time management for complex questions',
  ]

  const recommendations = [
    { title: 'System Design Bootcamp', time: '2 hours', difficulty: 'Hard', why: 'Your weakest area' },
    { title: 'Communication Skills', time: '1.5 hours', difficulty: 'Medium', why: 'Improve articulation' },
    { title: 'Advanced Algorithms', time: '3 hours', difficulty: 'Hard', why: 'Deepen knowledge' },
  ]

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
                        strokeDasharray: `${565.5 * (evaluation.overall_score / 100)} 565.5`,
                      }}
                    />
                  </svg>
                  <div className="results-score-text">
                    <span className="results-score-value">{Math.round(evaluation.overall_score)}%</span>
                    <span className="results-score-label">Overall Score</span>
                  </div>
                </div>
                <div className="results-score-details">
                  <div className="results-score-item">
                    <span>Performance</span>
                    <Badge variant={evaluation.overall_score >= 75 ? 'success' : evaluation.overall_score >= 60 ? 'warning' : 'error'}>
                      {getPerformanceRating(evaluation.overall_score)}
                    </Badge>
                  </div>
                  <div className="results-score-item">
                    <span>Technical Knowledge</span>
                    <span className="results-score-item-value">{Math.round(evaluation.technical_knowledge_score)}%</span>
                  </div>
                  <div className="results-score-item">
                    <span>Communication</span>
                    <span className="results-score-item-value">{Math.round(evaluation.communication_score)}%</span>
                  </div>
                  <div className="results-score-item">
                    <span>Problem Solving</span>
                    <span className="results-score-item-value">{Math.round(evaluation.problem_solving_score)}%</span>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Two Column Layout */}
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
                    {evaluation.categories.map((cat, idx) => (
                      <div key={idx} className="results-performance-item">
                        <div className="results-performance-header">
                          <span className="results-performance-name">{cat.name}</span>
                          <Badge variant={getScoreVariant(cat.score)} size="sm">{Math.round(cat.score)}%</Badge>
                        </div>
                        <Progress value={cat.score} color={getScoreVariant(cat.score)} showPercent={false} />
                        <p className="results-performance-feedback">{cat.feedback}</p>
                      </div>
                    ))}
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
