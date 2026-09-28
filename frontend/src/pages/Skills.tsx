import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { TrendingUp, TrendingDown, Minus, Lightbulb, ArrowRight, Filter, Download, Loader, AlertCircle } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { Progress } from '@/components/Progress'
import { interviewService, SkillAssessmentResponse } from '@/services/api'
import './Skills.css'

export const Skills: React.FC = () => {
  const [searchParams] = useSearchParams()
  const interviewId = searchParams.get('interview')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [skillAssessment, setSkillAssessment] = useState<SkillAssessmentResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSkillAssessment = async () => {
      if (!interviewId) {
        setError('Interview ID not found. Please view this page from an interview result.')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const assessment = await interviewService.getSkillAssessment(interviewId)
        setSkillAssessment(assessment)
        setError(null)
      } catch (err: any) {
        console.error('Failed to fetch skill assessment:', err)
        setError(err.message || 'Failed to load skill assessment')
      } finally {
        setLoading(false)
      }
    }

    fetchSkillAssessment()
  }, [interviewId])

  const getTrendIcon = (trend: string) => {
    if (trend === 'improving') return <TrendingUp size={16} className="skills-trend-icon up" />
    if (trend === 'declining') return <TrendingDown size={16} className="skills-trend-icon down" />
    return <Minus size={16} className="skills-trend-icon stable" />
  }

  const getLevelBadgeVariant = (level: number): 'success' | 'warning' | 'error' => {
    // level is 1-5 proficiency scale
    if (level >= 4) return 'success'
    if (level >= 3) return 'warning'
    return 'error'
  }

  const getLevelLabel = (level: number): string => {
    if (level >= 4) return 'Advanced'
    if (level >= 3) return 'Intermediate'
    return 'Beginner'
  }

  const getTrendBadgeVariant = (trend: string): 'success' | 'warning' | 'error' => {
    if (trend === 'improving') return 'success'
    if (trend === 'declining') return 'error'
    return 'warning'
  }

  const getConfidenceVariant = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 0.75) return 'success'
    if (confidence >= 0.5) return 'warning'
    return 'error'
  }

  const getProficiencyPercentage = (proficiency: number): number => {
    // Convert 1-5 scale to 0-100 percentage
    return (proficiency / 5) * 100
  }

  if (loading) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Skill Analysis' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="skills-page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
            <Loader size={32} className="animate-spin" />
            <span style={{ marginLeft: '16px' }}>Loading skill assessment...</span>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  if (error || !skillAssessment) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Skill Analysis' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="skills-page">
            <Card variant="default" padding="lg">
              <CardBody>
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <AlertCircle size={48} style={{ color: 'var(--color-error-500)', marginBottom: '16px' }} />
                  <h2>Unable to Load Skill Assessment</h2>
                  <p>{error || 'No skill assessment data available'}</p>
                </div>
              </CardBody>
            </Card>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  const categories = [
    { id: 'all', name: 'All Skills', count: skillAssessment.skills.length },
  ]

  // Add categories from the assessment
  Object.keys(skillAssessment.categories).forEach((cat) => {
    categories.push({
      id: cat.toLowerCase(),
      name: cat,
      count: skillAssessment.skills.filter(s => s.category === cat).length,
    })
  })

  const filteredSkills = skillAssessment.skills
  const averageConfidence = Math.round(
    filteredSkills.reduce((sum, s) => sum + s.confidence_score, 0) / filteredSkills.length * 100
  )

  return (
    <AppShell
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
                  <span className="skills-stat-label">Strongest Skills</span>
                  <span className="skills-stat-value positive">{skillAssessment.strongest_skills.length}</span>
                </div>
                <div className="skills-overview-stat">
                  <span className="skills-stat-label">Areas to Improve</span>
                  <span className="skills-stat-value negative">{skillAssessment.weakest_skills.length}</span>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Strongest Skills */}
          {skillAssessment.strongest_skills.length > 0 && (
            <Card variant="default" padding="lg">
              <CardHeader>
                <div className="skills-page-section-header">
                  <TrendingUp size={20} />
                  <h2>Your Strongest Skills</h2>
                </div>
              </CardHeader>
              <CardBody>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  {skillAssessment.strongest_skills.map((skill) => (
                    <Badge key={skill} variant="success" size="lg">{skill}</Badge>
                  ))}
                </div>
              </CardBody>
            </Card>
          )}

          {/* Weakest Skills */}
          {skillAssessment.weakest_skills.length > 0 && (
            <Card variant="default" padding="lg">
              <CardHeader>
                <div className="skills-page-section-header">
                  <AlertCircle size={20} />
                  <h2>Areas to Improve</h2>
                </div>
              </CardHeader>
              <CardBody>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  {skillAssessment.weakest_skills.map((skill) => (
                    <Badge key={skill} variant="error" size="lg">{skill}</Badge>
                  ))}
                </div>
              </CardBody>
            </Card>
          )}

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
                      <h3>{skill.skill_name}</h3>
                      <Badge variant={getLevelBadgeVariant(skill.current_proficiency)} size="sm">
                        {getLevelLabel(skill.current_proficiency)}
                      </Badge>
                    </div>
                    <div className="skills-page-skill-trend">
                      {getTrendIcon(skill.trend)}
                      <Badge variant={getTrendBadgeVariant(skill.trend)} size="sm">{skill.trend}</Badge>
                    </div>
                  </div>

                  <div className="skills-page-skill-confidence">
                    <Progress 
                      value={getProficiencyPercentage(skill.current_proficiency)} 
                      color={getConfidenceVariant(skill.confidence_score)} 
                      showPercent 
                    />
                  </div>

                  <div className="skills-page-skill-meta">
                    <span>Category: {skill.category}</span>
                    <span>Confidence: {Math.round(skill.confidence_score * 100)}%</span>
                  </div>

                  {skill.evidence.length > 0 && (
                    <div className="skills-page-skill-evidence">
                      <small>Evidence: {skill.evidence.slice(0, 2).join(', ')}{skill.evidence.length > 2 ? ', ...' : ''}</small>
                    </div>
                  )}

                  <div className="skills-page-skill-actions">
                    <Button variant="ghost" size="sm" icon={<ArrowRight size={14} />} iconPosition="right">
                      Practice
                    </Button>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>

          {/* Skill Gap Analysis */}
          {skillAssessment.skill_gap_analysis.length > 0 && (
            <Card variant="default" padding="lg" className="skills-page-development">
              <CardHeader>
                <div className="skills-page-section-header">
                  <Lightbulb size={20} />
                  <h2>Skill Gap Analysis</h2>
                </div>
              </CardHeader>
              <CardBody>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {skillAssessment.skill_gap_analysis.slice(0, 3).map((gap, idx) => (
                    <li key={idx} style={{ padding: '12px 0', borderBottom: idx < 2 ? '1px solid var(--color-border)' : 'none' }}>
                      {gap}
                    </li>
                  ))}
                </ul>
              </CardBody>
            </Card>
          )}
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Skills.displayName = 'Skills'
