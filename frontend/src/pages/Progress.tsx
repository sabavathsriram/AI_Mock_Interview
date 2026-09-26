import React from 'react'
import { TrendingUp, Award, Target, BookOpen, ArrowRight } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { ProgressChart, CircularProgress } from '@/components/charts'
import { mockStats, mockProgressData, mockSkills } from '@/data/mockData'
import './Progress.css'

export const Progress: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = React.useState(false)
  const strongestSkills = mockSkills
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 3)
  const weakestSkills = mockSkills
    .sort((a, b) => a.confidence - b.confidence)
    .slice(0, 3)

  const improvement = mockStats.bestScore - mockStats.worstScore

  const stats = [
    { icon: <TrendingUp size={24} />, label: 'Score Improvement', value: `+${improvement}%`, variant: 'success' as const },
    { icon: <Award size={24} />, label: 'Best Score', value: `${mockStats.bestScore}%`, variant: 'primary' as const },
    { icon: <Target size={24} />, label: 'Interviews', value: mockStats.totalInterviews, variant: 'secondary' as const },
    { icon: <BookOpen size={24} />, label: 'Completion Rate', value: `${mockStats.completionRate}%`, variant: 'warning' as const },
  ]

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Progress' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="progress-page">
          {/* Header */}
          <div className="progress-page-header">
            <div className="progress-page-header-content">
              <h1>Your Progress</h1>
              <p>Track your improvement over time</p>
            </div>
          </div>

          {/* Stats Overview */}
          <div className="progress-stats-grid">
            {stats.map((stat, index) => (
              <Card key={index} variant="default" padding="md" className="progress-stat-card">
                <CardBody>
                  <div className={`progress-stat-icon stat-${stat.variant}`}>
                    {stat.icon}
                  </div>
                  <p className="progress-stat-value">{stat.value}</p>
                  <p className="progress-stat-label">{stat.label}</p>
                </CardBody>
              </Card>
            ))}
          </div>

          {/* Progress Chart */}
          <Card variant="default" padding="lg" className="progress-chart-card">
            <CardHeader>
              <h2>Score Progress Over Time</h2>
            </CardHeader>
            <CardBody>
              <div className="progress-chart-container">
                <ProgressChart data={mockProgressData} height={300} />
              </div>
            </CardBody>
          </Card>

          {/* Before vs After & Frequency */}
          <div className="progress-comparison-grid">
            <Card variant="default" padding="lg" className="progress-comparison-card">
              <CardHeader>
                <h3>Before vs After</h3>
                <p className="progress-card-subtitle">First interview vs Latest</p>
              </CardHeader>
              <CardBody>
                <div className="progress-comparison-content">
                  <div className="progress-comparison-item">
                    <CircularProgress value={mockStats.worstScore} size={120} label="First Interview" />
                  </div>
                  <div className="progress-comparison-arrow">
                    <ArrowRight size={28} />
                  </div>
                  <div className="progress-comparison-item">
                    <CircularProgress value={mockStats.averageScore} size={120} label="Latest Interview" />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card variant="default" padding="lg" className="progress-frequency-card">
              <CardHeader>
                <h3>Interview Frequency</h3>
                <p className="progress-card-subtitle">This month</p>
              </CardHeader>
              <CardBody>
                <div className="progress-frequency-content">
                  <p className="progress-frequency-value">{mockStats.interviewsThisMonth}</p>
                  <p className="progress-frequency-label">interviews this month</p>
                  <Badge variant={mockStats.improvementTrend === 'positive' ? 'success' : 'error'} size="sm" className="progress-trend-badge">
                    {mockStats.improvementTrend === 'positive' ? '↑ Improving' : '↓ Declining'}
                  </Badge>
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Skills Comparison */}
          <div className="progress-skills-grid">
            <Card variant="default" padding="lg" className="progress-skills-card strongest">
              <CardHeader>
                <h3>
                  <Award size={20} />
                  Strongest Skills
                </h3>
              </CardHeader>
              <CardBody>
                <div className="progress-skills-list">
                  {strongestSkills.map((skill, index) => (
                    <div key={skill.name} className="progress-skill-item">
                      <span className="progress-skill-name">{skill.name}</span>
                      <Badge variant="success" size="sm">{skill.confidence}%</Badge>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card variant="default" padding="lg" className="progress-skills-card improve">
              <CardHeader>
                <h3>
                  <Target size={20} />
                  Skills to Improve
                </h3>
              </CardHeader>
              <CardBody>
                <div className="progress-skills-list">
                  {weakestSkills.map((skill) => (
                    <div key={skill.name} className="progress-skill-item">
                      <span className="progress-skill-name">{skill.name}</span>
                      <Badge variant="warning" size="sm">{skill.confidence}%</Badge>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Demo Notice */}
          <Card variant="default" padding="md" className="progress-demo-notice">
            <CardBody>
              <p>📊 <strong>Demo Data:</strong> Progress tracking is based on mock interview history.</p>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Progress.displayName = 'Progress'