import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, AlertCircle, Loader2, Check, FileText, Zap } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { resumeService, type ResumeDetailResponse, type ResumeIntelligenceResponse } from '@/services/api'
import './ResumeAnalysis.css'

export const ResumeAnalysis: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const [resume, setResume] = useState<ResumeDetailResponse | null>(null)
  const [intelligence, setIntelligence] = useState<ResumeIntelligenceResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadResume = async () => {
      if (!id) {
        setError('No resume ID provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const response = await resumeService.getResume(id)
        setResume(response.data)
        
        // Load intelligence profile if extraction is completed
        if (response.data.extraction_status === 'completed') {
          try {
            const intelligenceResponse = await resumeService.getResumeIntelligence(id)
            setIntelligence(intelligenceResponse.data)
          } catch (err) {
            console.log('Intelligence not yet available:', err)
          }
        }
        
        setError(null)
      } catch (err: any) {
        setError(err.message || 'Failed to load resume')
        console.error('Error loading resume:', err)
      } finally {
        setLoading(false)
      }
    }

    loadResume()
  }, [id])

  const handleAnalyzeResume = async () => {
    if (!id) return
    try {
      setAnalyzing(true)
      const response = await resumeService.analyzeResume(id)
      setIntelligence(response.data)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze resume')
      console.error('Error analyzing resume:', err)
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Resumes', href: '/resumes' },
          { label: 'Resume Analysis' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
            <Loader2 size={40} style={{ animation: 'spin 1s linear infinite' }} />
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  if (error || !resume) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Resumes', href: '/resumes' },
          { label: 'Resume Analysis' },
        ]}
      >
        <AppShellContent maxWidth="full">
          <div className="resume-analysis-page">
            <div className="resume-analysis-back">
              <Link to="/resumes">
                <Button variant="ghost" size="sm" icon={<ArrowLeft size={16} />} iconPosition="left">
                  Back to Resumes
                </Button>
              </Link>
            </div>

            <Card variant="default" padding="lg">
              <CardBody>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <strong>Error:</strong> {error || 'Resume not found'}
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Resumes', href: '/resumes' },
        { label: 'Resume Analysis' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="resume-analysis-page">
          {/* Back Button */}
          <div className="resume-analysis-back">
            <Link to="/resumes">
              <Button variant="ghost" size="sm" icon={<ArrowLeft size={16} />} iconPosition="left">
                Back to Resumes
              </Button>
            </Link>
          </div>

          {/* Resume Header */}
          <Card variant="elevated" padding="lg" style={{ marginBottom: '24px' }}>
            <CardBody>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ display: 'flex', gap: '16px', flex: 1 }}>
                  <FileText size={40} style={{ flexShrink: 0 }} />
                  <div>
                    <h2 style={{ margin: '0 0 8px 0' }}>{resume.filename}</h2>
                    <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                      {resume.file_size} bytes • {new Date(resume.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <Badge variant={resume.extraction_status === 'completed' ? 'success' : 'warning'}>
                  {resume.extraction_status === 'completed' ? <Check size={12} /> : <Loader2 size={12} />}
                  {resume.extraction_status}
                </Badge>
              </div>
            </CardBody>
          </Card>

          {/* Analysis Results */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
            {/* Extracted Text */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h3>Extracted Text</h3>
              </CardHeader>
              <CardBody>
                {resume.extracted_text ? (
                  <div 
                    style={{
                      backgroundColor: 'var(--color-bg-secondary)',
                      padding: '12px',
                      borderRadius: '4px',
                      fontSize: '13px',
                      fontFamily: 'monospace',
                      maxHeight: '300px',
                      overflowY: 'auto',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}
                  >
                    {resume.extracted_text}
                  </div>
                ) : (
                  <div style={{ color: 'var(--color-text-secondary)', padding: '12px', textAlign: 'center' }}>
                    {resume.extraction_status === 'completed' 
                      ? 'No text content extracted' 
                      : '⏳ Text extraction in progress...'}
                  </div>
                )}
              </CardBody>
            </Card>

            {/* Metadata */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h3>Document Metadata</h3>
              </CardHeader>
              <CardBody>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div>
                    <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>File Type</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>{resume.file_type.toUpperCase()}</p>
                  </div>
                  <div>
                    <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>File Size</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>
                      {(resume.file_size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <div>
                    <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>Uploaded</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>
                      {new Date(resume.uploaded_at).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>MIME Type</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>{resume.mime_type}</p>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Extraction Metadata */}
            {resume.extraction_metadata && Object.keys(resume.extraction_metadata).length > 0 && (
              <Card variant="default" padding="lg">
                <CardHeader>
                  <h3>Extraction Info</h3>
                </CardHeader>
                <CardBody>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {Object.entries(resume.extraction_metadata).map(([key, value]) => (
                      <div key={key}>
                        <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                          {key.replace(/_/g, ' ').charAt(0).toUpperCase() + key.replace(/_/g, ' ').slice(1)}
                        </p>
                        <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>
            )}
          </div>

          {/* Status Message */}
          {resume.extraction_status !== 'completed' && (
            <Card variant="default" padding="lg" style={{ marginTop: '24px', backgroundColor: 'var(--color-warning-50)' }}>
              <CardBody>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                  <p style={{ margin: 0 }}>
                    Your resume is being analyzed. Please check back soon for detailed insights.
                  </p>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Resume Intelligence Section */}
          {resume.extraction_status === 'completed' && (
            <div style={{ marginTop: '32px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <Zap size={24} style={{ color: 'var(--color-primary)' }} />
                <h2 style={{ margin: 0 }}>Resume Intelligence</h2>
              </div>

              {!intelligence || intelligence.status === 'pending' ? (
                <Card variant="default" padding="lg">
                  <CardBody>
                    <p style={{ margin: 0, marginBottom: '16px', color: 'var(--color-text-secondary)' }}>
                      Analyze your resume to extract structured candidate information including skills, education, experience, and more.
                    </p>
                    <Button 
                      variant="primary"
                      onClick={handleAnalyzeResume}
                      disabled={analyzing}
                      icon={analyzing ? <Loader2 size={16} /> : <Zap size={16} />}
                    >
                      {analyzing ? 'Analyzing Resume...' : 'Analyze Resume with AI'}
                    </Button>
                  </CardBody>
                </Card>
              ) : intelligence.status === 'analyzing' ? (
                <Card variant="default" padding="lg" style={{ backgroundColor: 'var(--color-info-50)' }}>
                  <CardBody>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                      <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                      <p style={{ margin: 0 }}>
                        Analyzing your resume... This may take a few moments.
                      </p>
                    </div>
                  </CardBody>
                </Card>
              ) : intelligence.status === 'failed' ? (
                <Card variant="default" padding="lg" style={{ backgroundColor: 'var(--color-error-50)' }}>
                  <CardBody>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                      <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                      <div>
                        <strong>Analysis Failed:</strong>
                        <p style={{ margin: '4px 0 0 0', fontSize: '14px' }}>{intelligence.error || 'Unknown error'}</p>
                        <Button
                          variant="primary"
                          size="sm"
                          style={{ marginTop: '12px' }}
                          onClick={handleAnalyzeResume}
                          disabled={analyzing}
                        >
                          Retry Analysis
                        </Button>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ) : intelligence.status === 'completed' && intelligence.profile ? (() => {
                const profile = intelligence.profile!
                return (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
                  {/* Candidate Info */}
                  {(profile.candidate_name || profile.contact) && (
                    <Card variant="default" padding="lg">
                      <CardHeader>
                        <h3>Candidate Information</h3>
                      </CardHeader>
                      <CardBody>
                        {profile.candidate_name && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>Name</p>
                            <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>{profile.candidate_name}</p>
                          </div>
                        )}
                        {profile.contact?.email && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>Email</p>
                            <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>{profile.contact.email}</p>
                          </div>
                        )}
                        {profile.contact?.phone && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>Phone</p>
                            <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>{profile.contact.phone}</p>
                          </div>
                        )}
                        {profile.contact?.location && (
                          <div>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)' }}>Location</p>
                            <p style={{ margin: '4px 0 0 0', fontWeight: 500 }}>{profile.contact.location}</p>
                          </div>
                        )}
                      </CardBody>
                    </Card>
                  )}

                  {/* Education */}
                  {profile.education && Array.isArray(profile.education) && profile.education.length > 0 && (
                    <Card variant="default" padding="lg">
                      <CardHeader>
                        <h3>Education</h3>
                      </CardHeader>
                      <CardBody>
                        {profile.education.map((edu: any, idx: number) => (
                          <div key={idx} style={{ marginBottom: idx < profile.education.length - 1 ? '12px' : 0 }}>
                            {edu.degree && <p style={{ margin: 0, fontWeight: 500 }}>{edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}</p>}
                            {edu.institution && <p style={{ margin: '2px 0', color: 'var(--color-text-secondary)', fontSize: '14px' }}>{edu.institution}</p>}
                            {(edu.graduation_year || edu.cgpa) && (
                              <p style={{ margin: '2px 0', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                                {edu.graduation_year && `Graduated ${edu.graduation_year}`}
                                {edu.cgpa && ` • CGPA: ${edu.cgpa}`}
                              </p>
                            )}
                          </div>
                        ))}
                      </CardBody>
                    </Card>
                  )}

                  {/* Skills */}
                  {profile.skills && (
                    <Card variant="default" padding="lg">
                      <CardHeader>
                        <h3>Technical Skills</h3>
                      </CardHeader>
                      <CardBody style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {profile.skills.programming_languages?.length > 0 && (
                          <div>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Programming Languages</p>
                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                              {profile.skills.programming_languages.map((lang: string) => (
                                <Badge key={lang} variant="primary">{lang}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        {profile.skills.frameworks?.length > 0 && (
                          <div>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Frameworks</p>
                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                              {profile.skills.frameworks.map((fw: string) => (
                                <Badge key={fw} variant="secondary">{fw}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        {profile.skills.databases?.length > 0 && (
                          <div>
                            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Databases</p>
                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                              {profile.skills.databases.map((db: string) => (
                                <Badge key={db}>{db}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </CardBody>
                    </Card>
                  )}

                  {/* Work Experience */}
                  {profile.experience && Array.isArray(profile.experience) && profile.experience.length > 0 && (
                    <Card variant="default" padding="lg">
                      <CardHeader>
                        <h3>Work Experience</h3>
                      </CardHeader>
                      <CardBody>
                        {profile.experience.map((exp: any, idx: number) => (
                          <div key={idx} style={{ marginBottom: idx < profile.experience.length - 1 ? '16px' : 0 }}>
                            {exp.position && <p style={{ margin: 0, fontWeight: 500 }}>{exp.position}</p>}
                            {exp.company && <p style={{ margin: '2px 0', color: 'var(--color-text-secondary)', fontSize: '14px' }}>{exp.company}</p>}
                            {(exp.duration || exp.start_year) && (
                              <p style={{ margin: '2px 0', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                                {exp.duration || `${exp.start_year}${exp.end_year ? ` - ${exp.end_year}` : ' - Present'}`}
                              </p>
                            )}
                            {exp.description && <p style={{ margin: '6px 0 0 0', fontSize: '13px' }}>{exp.description}</p>}
                          </div>
                        ))}
                      </CardBody>
                    </Card>
                  )}

                  {/* Projects */}
                  {profile.projects && Array.isArray(profile.projects) && profile.projects.length > 0 && (
                    <Card variant="default" padding="lg">
                      <CardHeader>
                        <h3>Projects</h3>
                      </CardHeader>
                      <CardBody>
                        {profile.projects.map((proj: any, idx: number) => (
                          <div key={idx} style={{ marginBottom: idx < profile.projects.length - 1 ? '12px' : 0 }}>
                            {proj.name && <p style={{ margin: 0, fontWeight: 500 }}>{proj.name}</p>}
                            {proj.description && <p style={{ margin: '4px 0', fontSize: '13px', color: 'var(--color-text-secondary)' }}>{proj.description}</p>}
                            {proj.technologies?.length > 0 && (
                              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '6px' }}>
                                {proj.technologies.map((tech: string) => (
                                  <Badge key={tech} variant="secondary" style={{ fontSize: '11px' }}>{tech}</Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </CardBody>
                    </Card>
                  )}
                </div>
                )
              })() : null}
            </div>
          )}
        </div>
      </AppShellContent>
    </AppShell>
  )
}

ResumeAnalysis.displayName = 'ResumeAnalysis'
