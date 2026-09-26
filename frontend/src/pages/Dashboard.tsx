import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  TrendingUp, 
  Zap, 
  BookOpen, 
  Award, 
  ArrowRight, 
  Sparkles, 
  Target, 
  Clock,
  BarChart3,
  CheckCircle,
  AlertCircle,
  ChevronRight
} from 'lucide-react'
import { AppShell, AppShellHeader, AppShellContent } from '@/components/layout'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/Card'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Progress } from '@/components/Progress'
import { Avatar } from '@/components/Avatar'
import './Dashboard.css'

interface DashboardStats {
  label: string
  value: string
  icon: React.ReactNode
  trend: string
  trendType: 'positive' | 'neutral'
}

interface RecentInterview {
  id: number
  title: string
  date: string
  score: number
  status: string
  category: string
}

interface SkillItem {
  name: string
  score: number
  progress: number
}

interface Recommendation {
  title: string
  description: string
  actionLabel: string
  href: string
  priority: 'high' | 'medium' | 'low'
}

export const Dashboard: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [userName] = useState('Alex Morgan')

  const stats: DashboardStats[] = [
    { label: 'Total Interviews', value: '12', icon: <Award size={24} />, trend: '+3 this month', trendType: 'positive' },
    { label: 'Average Score', value: '78%', icon: <TrendingUp size={24} />, trend: '+5% improvement', trendType: 'positive' },
    { label: 'Best Score', value: '92%', icon: <Sparkles size={24} />, trend: 'Data Structures', trendType: 'neutral' },
    { label: 'Skills Improved', value: '8', icon: <BookOpen size={24} />, trend: 'Last 30 days', trendType: 'positive' },
  ]

  const recentInterviews: RecentInterview[] = [
    { id: 1, title: 'Backend Engineer Interview', date: '2 days ago', score: 85, status: 'Completed', category: 'System Design' },
    { id: 2, title: 'Frontend Engineer Interview', date: '5 days ago', score: 72, status: 'Completed', category: 'React & State Management' },
    { id: 3, title: 'Full Stack Interview', date: '1 week ago', score: 88, status: 'Completed', category: 'APIs & Databases' },
  ]

  const skillCategories: SkillItem[] = [
    { name: 'Technical Skills', score: 82, progress: 82 },
    { name: 'Communication', score: 76, progress: 76 },
    { name: 'Problem Solving', score: 89, progress: 89 },
    { name: 'System Design', score: 65, progress: 65 },
    { name: 'Code Quality', score: 79, progress: 79 },
  ]

  const recommendations: Recommendation[] = [
    { title: 'Focus on System Design', description: 'Your weakest area. Practice scalability & distributed systems.', actionLabel: 'Start Practice', href: '/interview/setup', priority: 'high' },
    { title: 'Review Communication', description: 'Think-aloud practice will improve articulation during interviews.', actionLabel: 'Learn More', href: '/learning', priority: 'medium' },
    { title: 'Polish Your Resume', description: 'Update achievements and metrics for better interview alignment.', actionLabel: 'Edit Resume', href: '/resumes', priority: 'medium' },
  ]

  const breadcrumbs = [
    { label: 'Dashboard', href: '/dashboard' }
  ]

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'error'
  }

  const getPriorityBadgeVariant = (priority: string): 'error' | 'warning' | 'neutral' => {
    if (priority === 'high') return 'error'
    if (priority === 'medium') return 'warning'
    return 'neutral'
  }

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName={userName}
      userEmail="alex@example.com"
      breadcrumbs={breadcrumbs}
      showSidebar={true}
      showTopNav={true}
    >
      <AppShellContent maxWidth="full">
        {/* Page Header */}
        <div className="dashboard-page-header">
          <div className="dashboard-welcome">
            <h1>Welcome back, Alex 👋</h1>
            <p>Your interview readiness at a glance</p>
          </div>
          <Link to="/interview/setup">
            <Button variant="primary" size="lg" icon={<Zap size={20} />}>
              Start New Interview
            </Button>
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="dashboard-stats-grid">
          {stats.map((stat, idx) => (
            <Card key={idx} variant="elevated" padding="md">
              <CardBody>
                <div className="dashboard-stat-card">
                  <div className="dashboard-stat-icon">
                    {stat.icon}
                  </div>
                  <div className="dashboard-stat-content">
                    <span className="dashboard-stat-label">{stat.label}</span>
                    <span className="dashboard-stat-value">{stat.value}</span>
                    <span className={`dashboard-stat-trend ${stat.trendType}`}>{stat.trend}</span>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="dashboard-main-grid">
          {/* Interview Readiness - Prominent */}
          <Card variant="elevated" padding="lg" className="dashboard-readiness-card">
            <CardHeader>
              <div className="dashboard-readiness-header">
                <h2>Interview Readiness</h2>
                <Badge variant="primary" size="lg">78%</Badge>
              </div>
            </CardHeader>
            <CardBody>
              <div className="dashboard-readiness-content">
                <div className="dashboard-readiness-circle">
                  <svg viewBox="0 0 100 100" className="dashboard-progress-ring">
                    <circle 
                      cx="50" 
                      cy="50" 
                      r="45" 
                      fill="none" 
                      stroke="var(--color-border)" 
                      strokeWidth="8"
                    />
                    <circle 
                      cx="50" 
                      cy="50" 
                      r="45" 
                      fill="none" 
                      stroke="var(--color-primary-600)" 
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${282.7 * 0.78} 282.7`}
                      transform="rotate(-90 50 50)"
                    />
                  </svg>
                  <div className="dashboard-readiness-text">
                    <span className="dashboard-readiness-percent">78%</span>
                    <span className="dashboard-readiness-label">Ready</span>
                  </div>
                </div>
                <p className="dashboard-readiness-status">
                  You're ready for most interviews. Keep practicing System Design to reach 90%+
                </p>
              </div>
            </CardBody>
            <CardFooter>
              <Link to="/interview/setup" className="dashboard-readiness-action">
                <span>Take Interview Now</span>
                <ChevronRight size={16} />
              </Link>
            </CardFooter>
          </Card>

          {/* Skill Performance */}
          <Card variant="default" padding="lg">
            <CardHeader>
              <h2>Skill Performance</h2>
            </CardHeader>
            <CardBody>
              <div className="dashboard-skills-list">
                {skillCategories.map((skill, idx) => (
                  <div key={idx} className="dashboard-skill-item">
                    <div className="dashboard-skill-header">
                      <span className="dashboard-skill-name">{skill.name}</span>
                      <span className="dashboard-skill-score">{skill.score}%</span>
                    </div>
                    <Progress 
                      value={skill.progress} 
                      color={skill.progress >= 80 ? 'success' : skill.progress >= 60 ? 'warning' : 'error'}
                    />
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Recent Interviews */}
          <Card variant="default" padding="lg">
            <CardHeader>
              <div className="dashboard-section-header">
                <h2>Recent Interviews</h2>
                <Link to="/interview-history" className="dashboard-view-all">
                  View All
                  <ArrowRight size={16} />
                </Link>
              </div>
            </CardHeader>
            <CardBody>
              <div className="dashboard-interviews-list">
                {recentInterviews.map((interview) => (
                  <div key={interview.id} className="dashboard-interview-item">
                    <div className="dashboard-interview-info">
                      <h3>{interview.title}</h3>
                      <div className="dashboard-interview-meta">
                        <Badge variant="neutral" size="sm">{interview.category}</Badge>
                        <span className="dashboard-interview-date">{interview.date}</span>
                      </div>
                    </div>
                    <Badge 
                      variant={getScoreColor(interview.score) as 'success' | 'warning' | 'error'} 
                      size="lg"
                    >
                      {interview.score}%
                    </Badge>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* AI Recommendations */}
          <Card variant="default" padding="lg">
            <CardHeader>
              <div className="dashboard-section-header">
                <h2 className="dashboard-ai-title">
                  <Sparkles size={20} />
                  AI Recommendations
                </h2>
              </div>
            </CardHeader>
            <CardBody>
              <div className="dashboard-recommendations-list">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className={`dashboard-recommendation-card priority-${rec.priority}`}>
                    <div className="dashboard-rec-content">
                      <h3>{rec.title}</h3>
                      <p>{rec.description}</p>
                      <Badge variant={getPriorityBadgeVariant(rec.priority)} size="sm">
                        {rec.priority === 'high' ? 'High Priority' : rec.priority === 'medium' ? 'Medium Priority' : 'Low Priority'}
                      </Badge>
                    </div>
                    <Link to={rec.href} className="dashboard-rec-action">
                      {rec.actionLabel}
                      <ArrowRight size={16} />
                    </Link>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Quick Actions */}
          <Card variant="default" padding="lg">
            <CardHeader>
              <h2>Quick Actions</h2>
            </CardHeader>
            <CardBody>
              <div className="dashboard-actions-grid">
                <Link to="/interview/setup" className="dashboard-action-card">
                  <div className="dashboard-action-icon">
                    <Zap size={24} />
                  </div>
                  <span>Start Interview</span>
                </Link>
                <Link to="/skills" className="dashboard-action-card">
                  <div className="dashboard-action-icon">
                    <Target size={24} />
                  </div>
                  <span>View Skills</span>
                </Link>
                <Link to="/learning" className="dashboard-action-card">
                  <div className="dashboard-action-icon">
                    <BookOpen size={24} />
                  </div>
                  <span>Learning Path</span>
                </Link>
                <Link to="/resumes" className="dashboard-action-card">
                  <div className="dashboard-action-icon">
                    <Clock size={24} />
                  </div>
                  <span>My Resume</span>
                </Link>
              </div>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Dashboard.displayName = 'Dashboard'
