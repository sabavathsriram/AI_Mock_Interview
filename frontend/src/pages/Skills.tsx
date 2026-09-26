import React, { useState } from 'react'
import { TrendingUp, TrendingDown, Minus, Lightbulb, ArrowRight, Filter, Download } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { Progress } from '@/components/Progress'
import './Skills.css'

export const Skills: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [isDarkMode, setIsDarkMode] = useState(false)

  const skills = [
    { name: 'Data Structures', level: 'Advanced', confidence: 89, trend: 'improving', change: '+8%', lastAssessed: '2 days ago' },
    { name: 'Algorithms', level: 'Advanced', confidence: 85, trend: 'stable', change: '0%', lastAssessed: '3 days ago' },
    { name: 'System Design', level: 'Intermediate', confidence: 65, trend: 'declining', change: '-5%', lastAssessed: 'Today' },
    { name: 'Python', level: 'Advanced', confidence: 92, trend: 'improving', change: '+3%', lastAssessed: '1 week ago' },
    { name: 'JavaScript/TypeScript', level: 'Advanced', confidence: 88, trend: 'stable', change: '+1%', lastAssessed: '5 days ago' },
    { name: 'React', level: 'Advanced', confidence: 86, trend: 'improving', change: '+4%', lastAssessed: '1 week ago' },
    { name: 'Database Design', level: 'Intermediate', confidence: 72, trend: 'stable', change: '0%', lastAssessed: '2 weeks ago' },
    { name: 'Communication', level: 'Intermediate', confidence: 76, trend: 'improving', change: '+6%', lastAssessed: '4 days ago' },
  ]

  const categories = [
    { id: 'all', name: 'All Skills', count: 8 },
    { id: 'technical', name: 'Technical', count: 5 },
    { id: 'soft', name: 'Soft Skills', count: 3 },
  ]

  const getTrendIcon = (trend: string) => {
    if (trend === 'improving') return <TrendingUp size={16} className="skills-trend-icon up" />
    if (trend === 'declining') return <TrendingDown size={16} className="skills-trend-icon down" />
    return <Minus size={16} className="skills-trend-icon stable" />
  }

  const getLevelBadgeVariant = (level: string): 'success' | 'warning' | 'error' => {
    if (level === 'Advanced') return 'success'
    if (level === 'Intermediate') return 'warning'
    return 'error'
  }

  const getTrendBadgeVariant = (trend: string): 'success' | 'warning' | 'error' => {
    if (trend === 'improving') return 'success'
    if (trend === 'declining') return 'error'
    return 'warning'
  }

  const getConfidenceVariant = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 80) return 'success'
    if (confidence >= 60) return 'warning'
    return 'error'
  }

  const filteredSkills = skills
  const averageConfidence = Math.round(filteredSkills.reduce((sum, s) => sum + s.confidence, 0) / filteredSkills.length)

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Skill Analysis' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="skills-page">
          {/* Header */}
          <div className="skills-page-header">
            <div className="skills-page-header-content">
              <h1>Skill Intelligence</h1>
              <p>Track your skill development and identify growth opportunities</p>
            </div>
            <div className="skills-page-header-actions">
              <Button variant="ghost" size="sm" icon={<Filter size={18} />} title="Filter skills" />
              <Button variant="ghost" size="sm" icon={<Download size={18} />} title="Export report" />
            </div>
          </div>

          {/* Overview Card */}
          <Card variant="elevated" padding="lg" className="skills-overview-card">
            <CardBody>
              <div className="skills-overview-stats">
                <div className="skills-overview-stat">
                  <span className="skills-stat-label">Average Confidence</span>
                  <span className="skills-stat-value">{averageConfidence}%</span>
                </div>
                <div className="skills-overview-stat">
                  <span className="skills-stat-label">Total Skills Assessed</span>
                  <span className="skills-stat-value">{filteredSkills.length}</span>
                </div>
                <div className="skills-overview-stat">
                  <span className="skills-stat-label">Improving</span>
                  <span className="skills-stat-value positive">{filteredSkills.filter(s => s.trend === 'improving').length}</span>
                </div>
                <div className="skills-overview-stat">
                  <span className="skills-stat-label">Needs Work</span>
                  <span className="skills-stat-value negative">{filteredSkills.filter(s => s.confidence < 70).length}</span>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Category Tabs */}
          <div className="skills-page-tabs">
            {categories.map((cat) => (
              <button
                key={cat.id}
                className={`skills-page-tab ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat.id)}
              >
                <span>{cat.name}</span>
                <Badge variant="neutral" size="sm">{cat.count}</Badge>
              </button>
            ))}
          </div>

          {/* Skills Grid */}
          <div className="skills-page-grid">
            {filteredSkills.map((skill, idx) => (
              <Card key={idx} variant="default" padding="md" className="skills-page-skill-card">
                <CardBody>
                  <div className="skills-page-skill-header">
                    <div className="skills-page-skill-title">
                      <h3>{skill.name}</h3>
                      <Badge variant={getLevelBadgeVariant(skill.level)} size="sm">{skill.level}</Badge>
                    </div>
                    <div className="skills-page-skill-trend">
                      {getTrendIcon(skill.trend)}
                      <Badge variant={getTrendBadgeVariant(skill.trend)} size="sm">{skill.change}</Badge>
                    </div>
                  </div>

                  <div className="skills-page-skill-confidence">
                    <Progress value={skill.confidence} color={getConfidenceVariant(skill.confidence)} showPercent />
                  </div>

                  <div className="skills-page-skill-meta">
                    <span>Last assessed: {skill.lastAssessed}</span>
                  </div>

                  <div className="skills-page-skill-actions">
                    <Button variant="ghost" size="sm" icon={<ArrowRight size={14} />} iconPosition="right">
                      Practice
                    </Button>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>

          {/* Skill Development Path */}
          <Card variant="default" padding="lg" className="skills-page-development">
            <CardHeader>
              <div className="skills-page-section-header">
                <Lightbulb size={20} />
                <h2>Recommended Learning Path</h2>
              </div>
            </CardHeader>
            <CardBody>
              <div className="skills-page-recommendations">
                <div className="skills-page-rec-card high">
                  <div className="skills-page-rec-priority">
                    <Badge variant="error">High Priority</Badge>
                  </div>
                  <h3>Master System Design</h3>
                  <p>Your lowest-scoring area. System Design is critical for senior roles.</p>
                  <div className="skills-page-rec-details">
                    <span>⏱ 8-10 hours</span>
                    <Badge variant="error" size="sm">Hard</Badge>
                  </div>
                  <Button variant="primary" size="sm">Start Learning</Button>
                </div>

                <div className="skills-page-rec-card medium">
                  <div className="skills-page-rec-priority">
                    <Badge variant="warning">Medium Priority</Badge>
                  </div>
                  <h3>Deepen Database Knowledge</h3>
                  <p>Build on your intermediate skills with advanced database design patterns.</p>
                  <div className="skills-page-rec-details">
                    <span>⏱ 5-6 hours</span>
                    <Badge variant="warning" size="sm">Medium</Badge>
                  </div>
                  <Button variant="secondary" size="sm">Learn More</Button>
                </div>

                <div className="skills-page-rec-card maintenance">
                  <div className="skills-page-rec-priority">
                    <Badge variant="neutral">Maintenance</Badge>
                  </div>
                  <h3>Keep Your Skills Sharp</h3>
                  <p>Refresh advanced skills with weekly practice and coding challenges.</p>
                  <div className="skills-page-rec-details">
                    <span>⏱ 2-3 hours/week</span>
                    <Badge variant="neutral" size="sm">Varies</Badge>
                  </div>
                  <Button variant="secondary" size="sm">View Challenges</Button>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Skills.displayName = 'Skills'
