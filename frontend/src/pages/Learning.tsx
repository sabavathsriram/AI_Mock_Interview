import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { AlertCircle, Loader, BookOpen, Clock, Target, ExternalLink } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { interviewService, LearningRecommendationResponse } from '@/services/api'
import './Learning.css'

export const Learning: React.FC = () => {
  const [searchParams] = useSearchParams()
  const interviewId = searchParams.get('interview')
  const [recommendations, setRecommendations] = useState<LearningRecommendationResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!interviewId) {
        // No interview specified - show guidance
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const recs = await interviewService.getRecommendations(interviewId)
        setRecommendations(recs || [])
        setError(null)
      } catch (err: any) {
        console.error('Failed to fetch recommendations:', err)
        setError(err.message || 'Failed to load learning recommendations')
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [interviewId])

  const getPriorityVariant = (priority: number): 'success' | 'warning' | 'error' => {
    if (priority >= 4) return 'error'
    if (priority >= 2) return 'warning'
    return 'success'
  }

  const getPriorityLabel = (priority: number): string => {
    if (priority >= 4) return 'High Priority'
    if (priority >= 2) return 'Medium Priority'
    return 'Nice to Have'
  }
  return (
    <AppShell
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
          </div>

          {/* Loading State */}
          {loading && (
            <Card variant="default" padding="lg" className="learning-empty">
              <CardBody style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '16px', minHeight: '300px' }}>
                <Loader size={32} className="animate-spin" />
                <span>Loading learning recommendations...</span>
              </CardBody>
            </Card>
          )}

          {/* Error State */}
          {error && (
            <Card variant="default" padding="lg" className="learning-empty">
              <CardBody>
                <div className="learning-empty-content">
                  <AlertCircle size={48} />
                  <h3>Unable to Load Recommendations</h3>
                  <p>{error}</p>
                </div>
              </CardBody>
            </Card>
          )}

          {/* No Interview Selected */}
          {!loading && !error && !interviewId && (
            <Card variant="default" padding="lg" className="learning-empty">
              <CardBody>
                <div className="learning-empty-content">
                  <BookOpen size={48} />
                  <h3>No Learning Roadmap Available</h3>
                  <p>Please view this page from a completed interview to see personalized learning recommendations.</p>
                  <Link to="/interview-history">
                    <Button variant="primary" size="sm">
                      View Interview History
                    </Button>
                  </Link>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Recommendations */}
          {!loading && !error && interviewId && recommendations.length === 0 && (
            <Card variant="default" padding="lg" className="learning-empty">
              <CardBody>
                <div className="learning-empty-content">
                  <AlertCircle size={48} />
                  <h3>No Recommendations Yet</h3>
                  <p>Learning recommendations are still being generated. Please try again in a moment.</p>
                  <Link to="/interview-history">
                    <Button variant="primary" size="sm">
                      Back to History
                    </Button>
                  </Link>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Recommendations Grid */}
          {!loading && !error && recommendations.length > 0 && (
            <div className="learning-recommendations-grid">
              {recommendations.map((rec, idx) => (
                <Card key={idx} variant="default" padding="lg" className="learning-rec-card">
                  <CardHeader>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div>
                        <h3>{rec.title}</h3>
                        <p>{rec.description}</p>
                      </div>
                      <Badge variant={getPriorityVariant(rec.priority_level)} size="lg">
                        {getPriorityLabel(rec.priority_level)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardBody>
                    {/* Target Skills */}
                    <div className="learning-rec-section">
                      <h4>Target Skills</h4>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {rec.target_skills.map((skill) => (
                          <Badge key={skill} variant="neutral" size="sm">{skill}</Badge>
                        ))}
                      </div>
                    </div>

                    {/* Resources */}
                    <div className="learning-rec-section">
                      <h4>Resources</h4>
                      <div className="learning-resources-list">
                        {rec.resources.map((resource, ridx) => (
                          <div key={ridx} className="learning-resource-item">
                            <div className="learning-resource-header">
                              <span className="learning-resource-title">{resource.title}</span>
                              <div className="learning-resource-badges">
                                <Badge variant="neutral" size="sm">{resource.type}</Badge>
                                <Badge variant={resource.difficulty === 'Hard' ? 'error' : 'warning'} size="sm">
                                  {resource.difficulty}
                                </Badge>
                              </div>
                            </div>
                            <div className="learning-resource-meta">
                              {resource.estimated_time_hours && (
                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                  <Clock size={14} />
                                  {resource.estimated_time_hours}h
                                </span>
                              )}
                              <span>{resource.source}</span>
                              {resource.rating && <span>⭐ {resource.rating}/5</span>}
                            </div>
                            {resource.url && (
                              <a href={resource.url} target="_blank" rel="noopener noreferrer" className="learning-resource-link">
                                <Button variant="ghost" size="sm" icon={<ExternalLink size={14} />} iconPosition="right">
                                  Visit Resource
                                </Button>
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Completion Details */}
                    <div className="learning-rec-footer">
                      <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
                        <div>
                          <small>Estimated Time</small>
                          <strong>{rec.estimated_completion_time_hours}h</strong>
                        </div>
                        <div>
                          <small>Recommended Completion</small>
                          <strong>
                            {new Date(rec.recommended_completion_date).toLocaleDateString()}
                          </strong>
                        </div>
                      </div>
                      <Button variant="primary" size="sm">Start Learning</Button>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          )}
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Learning.displayName = 'Learning'