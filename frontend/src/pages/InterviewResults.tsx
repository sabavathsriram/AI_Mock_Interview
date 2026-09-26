import React, { useState } from 'react'
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
} from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Progress } from '@/components/Progress'
import './InterviewResults.css'

export const InterviewResults: React.FC = () => {
  const { id } = useParams()
  const [isDarkMode, setIsDarkMode] = useState(false)
  
  const overallScore = 78
  const date = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

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

  const getScoreVariant = (score: number): 'success' | 'warning' | 'error' => {
    if (score >= 75) return 'success'
    if (score >= 60) return 'warning'
    return 'error'
  }

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
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
              <p>Technical Interview • Hard • 45 minutes • {date}</p>
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
                        strokeDasharray: `${565.5 * (overallScore / 100)} 565.5`,
                      }}
                    />
                  </svg>
                  <div className="results-score-text">
                    <span className="results-score-value">{overallScore}%</span>
                    <span className="results-score-label">Overall Score</span>
                  </div>
                </div>
                <div className="results-score-details">
                  <div className="results-score-item">
                    <span>Performance</span>
                    <Badge variant="success">Excellent</Badge>
                  </div>
                  <div className="results-score-item">
                    <span>Percentile</span>
                    <span className="results-score-item-value">Top 20%</span>
                  </div>
                  <div className="results-score-item">
                    <span>Questions</span>
                    <span className="results-score-item-value">4/4 Answered</span>
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
                    {performanceByCategory.map((cat, idx) => (
                      <div key={idx} className="results-performance-item">
                        <div className="results-performance-header">
                          <span className="results-performance-name">{cat.name}</span>
                          <Badge variant={getScoreVariant(cat.score)} size="sm">{cat.score}%</Badge>
                        </div>
                        <Progress value={cat.score} color={getScoreVariant(cat.score)} showPercent={false} />
                        <p className="results-performance-feedback">{cat.feedback}</p>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>

              {/* Question Breakdown */}
              <Card variant="default" padding="lg">
                <CardHeader>
                  <h2>Question Breakdown</h2>
                </CardHeader>
                <CardBody>
                  <div className="results-questions-list">
                    {questions.map((q, idx) => (
                      <div key={idx} className={`results-question-item ${q.status}`}>
                        <div className="results-question-number">{q.num}</div>
                        <div className="results-question-info">
                          <p>{q.question}</p>
                          <Badge 
                            variant={q.status === 'excellent' ? 'success' : q.status === 'good' ? 'warning' : 'error'} 
                            size="sm"
                          >
                            {q.status === 'excellent' ? 'Excellent' : q.status === 'good' ? 'Good' : 'Needs Improvement'}
                          </Badge>
                        </div>
                        <Badge variant={getScoreVariant(q.score)} size="lg">{q.score}%</Badge>
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
                    {strengths.map((strength, idx) => (
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
                    {improvements.map((improvement, idx) => (
                      <li key={idx}>
                        <AlertCircle size={14} />
                        <span>{improvement}</span>
                      </li>
                    ))}
                  </ul>
                </CardBody>
              </Card>

              {/* Next Steps */}
              <Card variant="default" padding="lg">
                <CardHeader>
                  <div className="results-card-header">
                    <Lightbulb size={20} />
                    <h2>Recommended Learning Path</h2>
                  </div>
                </CardHeader>
                <CardBody>
                  <div className="results-recommendations">
                    {recommendations.map((rec, idx) => (
                      <button key={idx} className="results-recommendation-item">
                        <div className="results-rec-content">
                          <h4>{rec.title}</h4>
                          <div className="results-rec-meta">
                            <span>{rec.time}</span>
                            <Badge variant={rec.difficulty === 'Hard' ? 'error' : 'warning'} size="sm">
                              {rec.difficulty}
                            </Badge>
                          </div>
                          <p>{rec.why}</p>
                        </div>
                        <Target size={18} />
                      </button>
                    ))}
                  </div>
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
                  <h3>Great Progress!</h3>
                  <p>You've improved 12% since your last interview. Keep practicing and you'll be ready for any interview!</p>
                </div>
                <div className="results-footer-actions">
                  <Link to="/learning">
                    <Button variant="secondary" icon={<BookOpen size={18} />}>
                      View Learning Path
                    </Button>
                  </Link>
                  <Link to="/interview/setup">
                    <Button variant="primary" icon={<RefreshCw size={18} />}>
                      Next Interview
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
