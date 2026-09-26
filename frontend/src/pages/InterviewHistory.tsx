import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter, Calendar, Clock, Target, BarChart2, ChevronRight, Plus } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { Input } from '@/components/common'
import { mockInterviews } from '@/data/mockData'
import './InterviewHistory.css'

const filters = ['All', 'Technical', 'Behavioral', 'Coding', 'System Design']
const difficulties = ['Easy', 'Medium', 'Hard']

export const InterviewHistory: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('All')
  const [difficultyFilter, setDifficultyFilter] = useState('All')
  const [isDarkMode, setIsDarkMode] = useState(false)

  const filteredInterviews = mockInterviews.filter((interview) => {
    if (typeFilter !== 'All' && interview.type !== typeFilter) return false
    if (difficultyFilter !== 'All' && interview.difficulty !== difficultyFilter) return false
    return true
  })

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getScoreBadgeVariant = (score: number): 'success' | 'warning' | 'error' => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'error'
  }

  const getDifficultyBadgeVariant = (difficulty: string): 'success' | 'warning' | 'error' => {
    if (difficulty === 'Easy') return 'success'
    if (difficulty === 'Hard') return 'error'
    return 'warning'
  }

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
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
            <div className="interview-history-header-actions">
              <Link to="/interview/setup">
                <Button variant="primary" size="sm" icon={<Plus size={18} />} iconPosition="left">
                  New Interview
                </Button>
              </Link>
            </div>
          </div>

          {/* Filters */}
          <Card variant="default" padding="md" className="interview-history-filters-card">
            <CardBody>
              <div className="interview-history-filters">
                <div className="interview-history-search">
                  <Input
                    placeholder="Search interviews..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="interview-history-filter-buttons">
                  {filters.map((filter) => (
                    <button
                      key={filter}
                      className={`interview-history-filter-btn ${typeFilter === filter ? 'active' : ''}`}
                      onClick={() => setTypeFilter(filter)}
                    >
                      {filter}
                    </button>
                  ))}
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Interview List */}
          <div className="interview-history-list">
            {filteredInterviews.map((interview) => {
              const scoreVariant = getScoreBadgeVariant(interview.score)
              return (
                <Link key={interview.id} to={`/interview/${interview.id}/results`} className="interview-history-item-link">
                  <Card variant="default" padding="lg" className="interview-history-item-card">
                    <CardBody>
                      <div className="interview-history-item-header">
                        <div className="interview-history-item-score">
                          <span className={`interview-history-score-value score-${scoreVariant}`}>
                            {interview.score}
                          </span>
                        </div>
                        <div className="interview-history-item-main">
                          <div className="interview-history-item-title">
                            <h3>{interview.type} Interview</h3>
                            <div className="interview-history-item-badges">
                              <Badge variant={getDifficultyBadgeVariant(interview.difficulty)} size="sm">
                                {interview.difficulty}
                              </Badge>
                              <Badge variant={scoreVariant} size="sm">
                                {interview.score}%
                              </Badge>
                            </div>
                          </div>
                          <div className="interview-history-item-meta">
                            <span className="interview-history-meta-item">
                              <Calendar size={14} />
                              {formatDate(interview.startDate)}
                            </span>
                            <span className="interview-history-meta-item">
                              <Clock size={14} />
                              {interview.duration} min
                            </span>
                            <span className="interview-history-meta-item">
                              <Target size={14} />
                              {interview.skillEvaluated}
                            </span>
                          </div>
                        </div>
                        <div className="interview-history-item-arrow">
                          <ChevronRight size={20} />
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                </Link>
              )
            })}
          </div>

          {/* Empty State */}
          {filteredInterviews.length === 0 && (
            <Card variant="default" padding="lg" className="interview-history-empty">
              <CardBody>
                <div className="interview-history-empty-content">
                  <BarChart2 size={48} />
                  <h3>No interviews found</h3>
                  <p>Try adjusting your filters or start a new interview</p>
                  <Link to="/interview/setup">
                    <Button variant="primary" size="sm">
                      Start Interview
                    </Button>
                  </Link>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Demo Notice */}
          <Card variant="default" padding="md" className="interview-history-demo-notice">
            <CardBody>
              <p>📊 <strong>Demo Data:</strong> Interview history is populated with mock data for demonstration.</p>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

InterviewHistory.displayName = 'InterviewHistory'