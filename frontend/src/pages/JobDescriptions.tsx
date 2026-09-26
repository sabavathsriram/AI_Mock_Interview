import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Plus, 
  FileText, 
  Trash2, 
  Check, 
  X, 
  AlertTriangle, 
  TrendingUp,
  Briefcase,
  Target,
  ArrowRight,
  Sparkles
} from 'lucide-react'
import { AppShell, AppShellContent, AppShellHeader } from '@/components/layout'
import { Button } from '@/components/Button'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Input, TextArea } from '@/components'
import { Progress } from '@/components/Progress'
import { mockJobDescriptions, mockResumes } from '@/data/mockData'
import './JobDescriptions.css'

interface JobAlignment {
  matchScore: number
  matchedSkills: string[]
  missingSkills: string[]
  recommendations: string[]
}

export const JobDescriptions: React.FC = () => {
  const [showAddForm, setShowAddForm] = useState(false)
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)
  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null)
  const [isDarkMode, setIsDarkMode] = useState(false)
  
  const jobs = mockJobDescriptions
  const resumes = mockResumes

  // Mock alignment data
  const alignmentData: Record<string, JobAlignment> = {
    'job_001': {
      matchScore: 78,
      matchedSkills: ['Python', 'JavaScript', 'React', 'System Design', 'PostgreSQL'],
      missingSkills: ['AWS', 'Kubernetes', 'Machine Learning'],
      recommendations: [
        'Learn AWS fundamentals to improve cloud skills',
        'Add Kubernetes experience to your resume',
        'Consider a machine learning project'
      ]
    }
  }

  const selectedJob = jobs.find(j => j.id === selectedJobId)
  const currentAlignment = selectedJobId ? alignmentData[selectedJobId] : null

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getScoreColor = (score: number): 'success' | 'warning' | 'error' => {
    if (score >= 80) return 'success'
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
        { label: 'Job Descriptions' },
      ]}
    >
      <AppShellContent maxWidth="full">
        {/* Page Header */}
        <div className="jobs-page-header">
          <div className="jobs-header-content">
            <h1>Job Alignment</h1>
            <p>Match your resume to job descriptions and identify skill gaps</p>
          </div>
          <Button 
            variant="primary" 
            size="lg" 
            icon={<Plus size={20} />} 
            onClick={() => setShowAddForm(!showAddForm)}
          >
            Add Job Description
          </Button>
        </div>

        {/* Add Form */}
        {showAddForm && (
          <Card variant="elevated" padding="lg" className="jobs-add-form">
            <CardHeader>
              <h2>Add New Job Description</h2>
            </CardHeader>
            <CardBody>
              <div className="jobs-form-grid">
                <Input label="Job Title" placeholder="e.g., Senior Software Engineer" />
                <Input label="Company" placeholder="e.g., Google" />
              </div>
              <div className="jobs-form-full">
                <TextArea label="Job Description" placeholder="Paste job description..." rows={6} />
              </div>
              <div className="jobs-form-grid">
                <Input label="Required Skills (comma-separated)" placeholder="Python, JavaScript, React..." />
                <Input label="Preferred Skills (comma-separated)" placeholder="AWS, Docker, System Design..." />
              </div>
              <div className="jobs-form-actions">
                <Button variant="primary">Save Job Description</Button>
                <Button variant="secondary" onClick={() => setShowAddForm(false)}>Cancel</Button>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Main Content - Two Columns */}
        <div className="jobs-main-grid">
          {/* Left Column - Job List */}
          <div className="jobs-list-section">
            <h2 className="jobs-section-title">Job Descriptions</h2>
            
            {jobs.length === 0 ? (
              <Card variant="default" padding="lg">
                <CardBody>
                  <div className="jobs-empty">
                    <FileText size={48} />
                    <h3>No job descriptions yet</h3>
                    <p>Add a job description to practice targeted interviews</p>
                    <Button variant="primary" onClick={() => setShowAddForm(true)}>Add First Job</Button>
                  </div>
                </CardBody>
              </Card>
            ) : (
              <div className="jobs-list">
                {jobs.map((job) => (
                  <Card 
                    key={job.id} 
                    variant={selectedJobId === job.id ? 'elevated' : 'default'} 
                    padding="md"
                    className={`jobs-card ${selectedJobId === job.id ? 'selected' : ''}`}
                    onClick={() => setSelectedJobId(job.id)}
                  >
                    <CardBody>
                      <div className="jobs-card-header">
                        <div>
                          <h3>{job.title}</h3>
                          <p>{job.company}</p>
                        </div>
                        {selectedJobId === job.id && (
                          <Badge variant="primary">Selected</Badge>
                        )}
                      </div>
                      
                      <div className="jobs-card-skills">
                        <div className="jobs-skill-group">
                          <span className="jobs-skill-label">Required:</span>
                          <div className="jobs-skill-tags">
                            {job.requiredSkills.slice(0, 3).map((skill) => (
                              <Badge key={skill} variant="neutral" size="sm">{skill}</Badge>
                            ))}
                            {job.requiredSkills.length > 3 && (
                              <Badge variant="neutral" size="sm">+{job.requiredSkills.length - 3}</Badge>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="jobs-card-meta">
                        <span>{job.yearsRequired} years exp.</span>
                        <span>•</span>
                        <span>Saved: {formatDate(job.savedDate)}</span>
                      </div>
                    </CardBody>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Right Column - Alignment Analysis */}
          <div className="jobs-alignment-section">
            <h2 className="jobs-section-title">Resume Alignment</h2>
            
            {!selectedJobId ? (
              <Card variant="default" padding="lg">
                <CardBody>
                  <div className="jobs-alignment-empty">
                    <Target size={48} />
                    <h3>Select a Job Description</h3>
                    <p>Click on a job to see how your resume matches</p>
                  </div>
                </CardBody>
              </Card>
            ) : currentAlignment ? (
              <div className="jobs-alignment-content">
                {/* Overall Score */}
                <Card variant="elevated" padding="lg">
                  <CardBody>
                    <div className="jobs-alignment-header">
                      <div>
                        <h3>Match Score</h3>
                        <p>How well your resume matches this role</p>
                      </div>
                      <Badge 
                        variant={getScoreColor(currentAlignment.matchScore)} 
                        size="lg"
                      >
                        {currentAlignment.matchScore}%
                      </Badge>
                    </div>
                    <Progress 
                      value={currentAlignment.matchScore} 
                      color={getScoreColor(currentAlignment.matchScore)}
                    />
                  </CardBody>
                </Card>

                {/* Matched Skills */}
                <Card variant="default" padding="lg">
                  <CardHeader>
                    <div className="jobs-skill-header">
                      <Check size={20} />
                      <h3>Matched Skills</h3>
                    </div>
                  </CardHeader>
                  <CardBody>
                    <div className="jobs-skill-list">
                      {currentAlignment.matchedSkills.map((skill) => (
                        <div key={skill} className="jobs-skill-item matched">
                          <Check size={14} />
                          <span>{skill}</span>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>

                {/* Missing Skills */}
                <Card variant="default" padding="lg">
                  <CardHeader>
                    <div className="jobs-skill-header missing">
                      <AlertTriangle size={20} />
                      <h3>Skill Gaps</h3>
                    </div>
                  </CardHeader>
                  <CardBody>
                    <div className="jobs-skill-list">
                      {currentAlignment.missingSkills.map((skill) => (
                        <div key={skill} className="jobs-skill-item missing">
                          <X size={14} />
                          <span>{skill}</span>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>

                {/* Recommendations */}
                <Card variant="default" padding="lg">
                  <CardHeader>
                    <div className="jobs-skill-header ai">
                      <Sparkles size={20} />
                      <h3>AI Recommendations</h3>
                    </div>
                  </CardHeader>
                  <CardBody>
                    <div className="jobs-recommendations">
                      {currentAlignment.recommendations.map((rec, idx) => (
                        <div key={idx} className="jobs-recommendation">
                          <span className="jobs-rec-number">{idx + 1}</span>
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>

                {/* Action */}
                <Link to="/interview/setup" className="jobs-action-link">
                  <Button variant="primary" size="lg" icon={<ArrowRight size={20} />} fullWidth>
                    Practice Interview for This Role
                  </Button>
                </Link>
              </div>
            ) : (
              <Card variant="default" padding="lg">
                <CardBody>
                  <div className="jobs-alignment-empty">
                    <TrendingUp size={48} />
                    <h3>Analysis Ready</h3>
                    <p>Resume analysis will appear here</p>
                  </div>
                </CardBody>
              </Card>
            )}
          </div>
        </div>

        {/* Demo Notice */}
        <div className="jobs-demo-notice">
          <AlertTriangle size={20} />
          <div>
            <p className="jobs-notice-title">Demo Data Notice</p>
            <p className="jobs-notice-text">
              This page shows mock job descriptions and alignment analysis for demonstration purposes.
            </p>
          </div>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

JobDescriptions.displayName = 'JobDescriptions'