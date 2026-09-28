import React, { useState, useEffect } from 'react'
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
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/contexts/ThemeContext'
import { userService, interviewService } from '@/services/api'
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
  const { user, logout } = useAuth()
  const { isDarkMode, toggleDarkMode } = useTheme()
  
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats[]>([])
  const [recentInterviews, setRecentInterviews] = useState<RecentInterview[]>([])
  const [skillCategories, setSkillCategories] = useState<SkillItem[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [readinessScore, setReadinessScore] = useState(0)

  // Get user info from auth context
  const userName = user?.full_name || 'User'
  const userEmail = user?.email || ''

  // Fetch dashboard data from backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)

        // Note: User stats and interview history endpoints not yet implemented in backend
        // Showing empty state instead of mock data
        setStats([])
        setSkillCategories([])
        setRecommendations([])
        setRecentInterviews([])

      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  // Helper function to format dates
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) return '1 day ago'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`
    return `${Math.floor(diffDays / 30)} month${Math.floor(diffDays / 30) > 1 ? 's' : ''} ago`
  }

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
      breadcrumbs={breadcrumbs}
      showSidebar={true}
      showTopNav={true}
    >
      <AppShellContent maxWidth="full">
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
            <p>Loading dashboard...</p>
          </div>
        ) : (
          <>
            {/* Page Header */}
            <div className="dashboard-page-header">
              <div className="dashboard-welcome">
                <h1>Welcome back, {userName.split(' ')[0]} 👋</h1>
                <p>Your interview readiness at a glance</p>
              </div>
              <Link to="/interview/setup">
                <Button variant="primary" size="lg" icon={<Zap size={20} />}>
                  Start New Interview
                </Button>
              </Link>
            </div>

            {/* Empty State - No data available yet */}
            {stats.length === 0 && skillCategories.length === 0 && recentInterviews.length === 0 && recommendations.length === 0 ? (
              <div style={{ 
                padding: '60px 20px', 
                textAlign: 'center', 
                color: 'var(--color-text-secondary)' 
              }}>
                <Award size={64} style={{ marginBottom: '20px', opacity: 0.5 }} />
                <h2 style={{ marginBottom: '10px', color: 'var(--color-text-primary)' }}>No Interview Data Yet</h2>
                <p style={{ marginBottom: '30px' }}>Start your first mock interview to begin building your performance profile.</p>
                <Link to="/interview/setup">
                  <Button variant="primary" size="lg" icon={<Zap size={20} />}>
                    Start First Interview
                  </Button>
                </Link>
              </div>
            ) : (
              <>
                {/* Stats Grid - Only show if we have data */}
                {stats.length > 0 && (
                  <div className="dashboard-stats-grid">
                    {stats.map((stat, idx) => (
                      <div key={idx} className="dashboard-stat-card">
                        <div className="dashboard-stat-icon">
                          {stat.icon}
                        </div>
                        <div className="dashboard-stat-content">
                          <span className="dashboard-stat-label">{stat.label}</span>
                          <span className="dashboard-stat-value">{stat.value}</span>
                          <span className={`dashboard-stat-trend ${stat.trendType}`}>{stat.trend}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </>
        )}
      </AppShellContent>
    </AppShell>
  )
}

Dashboard.displayName = 'Dashboard'
