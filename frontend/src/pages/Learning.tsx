import React from 'react'
import { Link } from 'react-router-dom'
import {
  BookOpen,
  PlayCircle,
  ArrowRight,
} from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { Progress } from '@/components/Progress'
import { mockLearningRoadmap } from '@/data/mockData'
import './Learning.css'

export const Learning: React.FC = () => {
  const roadmap = mockLearningRoadmap
  const [isDarkMode, setIsDarkMode] = React.useState(false)

  const inProgress = roadmap.filter(item => item.status === 'In Progress').length
  const completed = roadmap.filter(item => item.status === 'Completed').length
  const notStarted = roadmap.filter(item => item.status === 'Not Started').length

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' => {
    if (status === 'Completed') return 'success'
    if (status === 'In Progress') return 'warning'
    return 'error'
  }

  const getLevelProgress = (current: string, target: string): number => {
    const levels: Record<string, number> = { Beginner: 1, Intermediate: 2, Advanced: 3, Expert: 4 }
    const curr = levels[current] || 0
    const targ = levels[target] || 0
    return (curr / targ) * 100
  }

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Learning Roadmap' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="learning-page">
          {/* Header */}
          <div className="learning-page-header">
            <div className="learning-page-header-content">
              <h1>Your Learning Roadmap</h1>
              <p>Personalized learning path based on your interview performance</p>
            </div>
            <div className="learning-page-header-actions">
              <Link to="/learning/resources">
                <Button variant="primary" size="sm" icon={<BookOpen size={18} />} iconPosition="left">
                  Browse Resources
                </Button>
              </Link>
            </div>
          </div>

          {/* Progress Overview */}
          <Card variant="elevated" padding="lg" className="learning-overview-card">
            <CardBody>
              <div className="learning-overview-stats">
                <div className="learning-overview-stat">
                  <span className="learning-stat-label">In Progress</span>
                  <span className="learning-stat-value">{inProgress}</span>
                </div>
                <div className="learning-overview-stat">
                  <span className="learning-stat-label">Completed</span>
                  <span className="learning-stat-value positive">{completed}</span>
                </div>
                <div className="learning-overview-stat">
                  <span className="learning-stat-label">Not Started</span>
                  <span className="learning-stat-value">{notStarted}</span>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Roadmap Cards */}
          <div className="learning-roadmap-list">
            {roadmap.map((item) => (
              <Card key={item.id} variant="default" padding="lg" className={`learning-roadmap-card ${item.status === 'In Progress' ? 'active' : ''}`}>
                <CardBody>
                  <div className="learning-roadmap-header">
                    <div className="learning-roadmap-title">
                      <h3>{item.topic}</h3>
                      <Badge variant={getStatusColor(item.status)} size="sm">{item.status}</Badge>
                    </div>
                    <p className="learning-roadmap-description">{item.whyRecommended}</p>
                  </div>

                  <div className="learning-roadmap-meta">
                    <div className="learning-roadmap-meta-item">
                      <span className="learning-meta-label">Current Level</span>
                      <span className="learning-meta-value">{item.currentLevel}</span>
                    </div>
                    <div className="learning-roadmap-meta-item">
                      <span className="learning-meta-label">Target Level</span>
                      <span className="learning-meta-value">{item.targetLevel}</span>
                    </div>
                    <div className="learning-roadmap-meta-item">
                      <span className="learning-meta-label">Est. Effort</span>
                      <span className="learning-meta-value">{item.estimatedEffort}</span>
                    </div>
                    <div className="learning-roadmap-meta-item">
                      <span className="learning-meta-label">Resources</span>
                      <span className="learning-meta-value">{item.resources.length}</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {item.status === 'In Progress' && (
                    <div className="learning-roadmap-progress">
                      <span className="learning-progress-label">Progress</span>
                      <Progress value={getLevelProgress(item.currentLevel, item.targetLevel)} color="warning" showPercent />
                    </div>
                  )}

                  {/* Concepts */}
                  <div className="learning-roadmap-concepts">
                    <span className="learning-concepts-label">Key Concepts</span>
                    <div className="learning-concepts-tags">
                      {item.concepts.map((concept, i) => (
                        <Badge key={i} variant="neutral" size="sm">{concept}</Badge>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="learning-roadmap-actions">
                    <Button variant="primary" size="sm" icon={<PlayCircle size={14} />} iconPosition="left">
                      {item.status === 'Not Started' ? 'Start Learning' : 'Continue'}
                    </Button>
                    <Link to="/learning/resources">
                      <Button variant="secondary" size="sm" icon={<BookOpen size={14} />} iconPosition="left">
                        View Resources
                      </Button>
                    </Link>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>

          {/* Demo Notice */}
          <Card variant="default" padding="md" className="learning-demo-notice">
            <CardBody>
              <p>📊 <strong>Demo Data:</strong> Learning roadmap is based on mock interview performance data.</p>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Learning.displayName = 'Learning'