import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Zap,
  Clock,
  FileText,
  Target,
  BarChart2,
  Play,
  Check,
  AlertCircle,
  AlertTriangle,
} from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Button } from '@/components/common'
import { Card, CardHeader, CardBody } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { useAuth } from '@/contexts/AuthContext'
import { interviewService, resumeService } from '@/services/api'
import './InterviewSetup.css'

const interviewTypes = [
  { value: 'technical', label: 'Technical', desc: 'Core CS, data structures, algorithms' },
  { value: 'behavioral', label: 'Behavioral', desc: 'Soft skills, leadership scenarios' },
  { value: 'system_design', label: 'System Design', desc: 'Scalable system architecture' },
  { value: 'coding', label: 'Coding', desc: 'Live coding challenges' },
]

const difficulties = ['easy', 'medium', 'hard', 'expert']
const durations = [15, 30, 45, 60]

export const InterviewSetup: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resumes, setResumes] = useState<any[]>([])
  const [resumesLoading, setResumesLoading] = useState(true)
  
  const [config, setConfig] = useState({
    interview_type: 'technical',
    difficulty_level: 'medium',
    duration_minutes: 30,
    question_count: 10,
    target_position: '',
    target_company: '',
    resume_id: '',
  })

  // Load resumes on mount
  useEffect(() => {
    const loadResumes = async () => {
      try {
        setResumesLoading(true)
        const response = await resumeService.listResumes()
        const resumeList = response.data.resumes || []
        setResumes(resumeList)
        
        // Auto-select first resume with completed extraction
        const extractedResume = resumeList.find((r: any) => r.extraction_status === 'completed')
        if (extractedResume) {
          setConfig((prev) => ({ ...prev, resume_id: extractedResume.id }))
        }
      } catch (err) {
        console.error('Failed to load resumes:', err)
        setError('Failed to load resumes. Please refresh the page.')
      } finally {
        setResumesLoading(false)
      }
    }
    
    loadResumes()
  }, [])

  const canStart = config.target_position.trim().length > 0 && config.resume_id && !loading

  // Get selected resume for status checking
  const selectedResume = resumes.find((r: any) => r.id === config.resume_id)
  const isResumeReady = selectedResume?.extraction_status === 'completed'

  const handleStart = async () => {
    if (!canStart || !user) return
    
    // Additional validation for resume status
    if (!isResumeReady) {
      setError('Selected resume is not ready. Please select a resume with completed extraction.')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      // Step 1: Start interview session (generates questions internally)
      const sessionResponse = await interviewService.startInterview({
        resume_id: config.resume_id,
        interview_type: config.interview_type,
        target_position: config.target_position,
        target_company: config.target_company || undefined,
        difficulty: config.difficulty_level,
        duration_minutes: config.duration_minutes,
        num_questions: config.question_count,
      })
      
      if (!sessionResponse.session_id) {
        throw new Error('Failed to create interview session')
      }
      
      // Redirect to interview session with state
      navigate(`/interview/${sessionResponse.session_id}/question`, {
        state: { firstQuestion: sessionResponse.current_question }
      })
    } catch (err: any) {
      // Extract error message from API response
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to start interview'
      setError(errorMessage)
      setLoading(false)
    }
  }

  const getDifficultyBadgeVariant = (diff: string): 'success' | 'warning' | 'error' | 'primary' => {
    if (diff === 'easy') return 'success'
    if (diff === 'hard') return 'error'
    if (diff === 'expert') return 'primary'
    return 'warning'
  }

  const difficultyDescriptions: Record<string, string> = {
    'expert': 'Expert-level questions throughout',
    'easy': 'Easy-level questions throughout',
    'medium': 'Mix of medium difficulty',
    'hard': 'Hard-level questions throughout',
  }

  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Mock Interview', href: '/interview/setup' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="interview-page-header">
          <div className="interview-header-content">
            <h1>Setup Your Interview</h1>
            <p>Configure your mock interview parameters</p>
          </div>
        </div>

        {error && (
          <Card variant="default" padding="md" className="error-card">
            <CardBody>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Error:</strong> {error}
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {!config.resume_id && !resumesLoading && resumes.length > 0 && (
          <Card variant="default" padding="md" className="warning-card">
            <CardBody>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '2px', color: '#ff9800' }} />
                <div>
                  <strong>Resume Required:</strong> Please select a resume to generate personalized interview questions.
                </div>
              </div>
            </CardBody>
          </Card>
        )}
        
        {config.resume_id && !isResumeReady && (
          <Card variant="default" padding="md" className="warning-card">
            <CardBody>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '2px', color: '#ff9800' }} />
                <div>
                  <strong>Resume Not Ready:</strong> The selected resume is still being processed or extraction failed. 
                  {selectedResume?.extraction_status === 'pending' && ' Please wait for extraction to complete.'}
                  {selectedResume?.extraction_status === 'failed' && ' Extraction failed. Please re-upload the resume.'}
                  {!selectedResume?.extraction_status && ' Status unknown. Please select a different resume or re-upload.'}
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        <div className="interview-main-grid">
          <div className="interview-config-section">
            {/* Resume Selection */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Select Resume</h2>
                <p>Choose the resume to base your interview questions on</p>
              </CardHeader>
              <CardBody>
                {resumesLoading ? (
                  <div style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                    Loading resumes...
                  </div>
                ) : resumes.length === 0 ? (
                  <div style={{ padding: '20px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                    <p>No resumes found. Please upload a resume first.</p>
                  </div>
                ) : (
                  <select
                    value={config.resume_id}
                    onChange={(e) => setConfig((prev) => ({ ...prev, resume_id: e.target.value }))}
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '14px',
                      fontFamily: 'inherit',
                      backgroundColor: 'var(--color-bg-secondary)',
                    }}
                  >
                    <option value="">Select a resume...</option>
                    {resumes.map((resume: any) => {
                      const status = resume.extraction_status || 'unknown'
                      let statusText = ''
                      if (status === 'completed') {
                        statusText = ' ✓'
                      } else if (status === 'pending') {
                        statusText = ' (Processing...)'
                      } else if (status === 'failed') {
                        statusText = ' (Extraction Failed)'
                      } else {
                        statusText = ' (Not Extracted)'
                      }
                      
                      return (
                        <option 
                          key={resume.id} 
                          value={resume.id}
                          disabled={status !== 'completed'}
                        >
                          {resume.filename || resume.display_name || 'Untitled'}{statusText}
                        </option>
                      )
                    })}
                  </select>
                )}
              </CardBody>
            </Card>

            {/* Interview Type */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Interview Type</h2>
                <p>Select the type of interview you want to practice</p>
              </CardHeader>
              <CardBody>
                <div className="interview-type-grid">
                  {interviewTypes.map((type) => (
                    <button
                      key={type.value}
                      onClick={() => setConfig((prev) => ({ ...prev, interview_type: type.value }))}
                      className={`interview-type-card ${config.interview_type === type.value ? 'selected' : ''}`}
                      disabled={loading}
                    >
                      <div className="interview-type-header">
                        <span className="interview-type-label">{type.label}</span>
                        {config.interview_type === type.value && (
                          <Check size={18} className="interview-type-check" />
                        )}
                      </div>
                      <p className="interview-type-desc">{type.desc}</p>
                    </button>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Target Position */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Target Position</h2>
                <p>What position are you interviewing for?</p>
              </CardHeader>
              <CardBody>
                <input
                  type="text"
                  placeholder="e.g., Senior Software Engineer, Product Manager..."
                  value={config.target_position}
                  onChange={(e) => setConfig((prev) => ({ ...prev, target_position: e.target.value }))}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                  }}
                />
              </CardBody>
            </Card>

            {/* Target Company */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Target Company (Optional)</h2>
              </CardHeader>
              <CardBody>
                <input
                  type="text"
                  placeholder="e.g., Google, Microsoft, startup..."
                  value={config.target_company}
                  onChange={(e) => setConfig((prev) => ({ ...prev, target_company: e.target.value }))}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                  }}
                />
              </CardBody>
            </Card>

            {/* Difficulty */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Difficulty Level</h2>
              </CardHeader>
              <CardBody>
                <div className="interview-difficulty-options">
                  {difficulties.map((diff) => (
                    <button
                      key={diff}
                      onClick={() => setConfig((prev) => ({ ...prev, difficulty_level: diff }))}
                      className={`interview-difficulty-btn ${config.difficulty_level === diff ? 'selected' : ''}`}
                      disabled={loading}
                    >
                      {diff.charAt(0).toUpperCase() + diff.slice(1)}
                    </button>
                  ))}
                </div>
                <p className="interview-difficulty-desc">
                  {difficultyDescriptions[config.difficulty_level]}
                </p>
              </CardBody>
            </Card>

            {/* Duration */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <div className="interview-duration-header">
                  <Clock size={20} />
                  <h2>Interview Duration</h2>
                </div>
              </CardHeader>
              <CardBody>
                <div className="interview-duration-grid">
                  {durations.map((dur) => (
                    <button
                      key={dur}
                      onClick={() => setConfig((prev) => ({ ...prev, duration_minutes: dur }))}
                      className={`interview-duration-card ${config.duration_minutes === dur ? 'selected' : ''}`}
                      disabled={loading}
                    >
                      <span className="interview-duration-value">{dur}</span>
                      <span className="interview-duration-label">min</span>
                    </button>
                  ))}
                </div>
                <p className="interview-duration-estimate">
                  Estimated: ~{Math.floor(config.duration_minutes / 3)} questions
                </p>
              </CardBody>
            </Card>

            {/* Question Count */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Number of Questions</h2>
              </CardHeader>
              <CardBody>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <button
                    onClick={() => setConfig((prev) => ({ ...prev, question_count: Math.max(5, prev.question_count - 1) }))}
                    disabled={loading || config.question_count <= 5}
                    style={{ padding: '8px 12px' }}
                  >
                    −
                  </button>
                  <input
                    type="number"
                    min="5"
                    max="50"
                    value={config.question_count}
                    onChange={(e) => {
                      const val = Math.min(50, Math.max(5, parseInt(e.target.value) || 5))
                      setConfig((prev) => ({ ...prev, question_count: val }))
                    }}
                    disabled={loading}
                    style={{
                      width: '60px',
                      padding: '8px 10px',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)',
                      textAlign: 'center',
                      fontSize: '14px',
                    }}
                  />
                  <button
                    onClick={() => setConfig((prev) => ({ ...prev, question_count: Math.min(50, prev.question_count + 1) }))}
                    disabled={loading || config.question_count >= 50}
                    style={{ padding: '8px 12px' }}
                  >
                    +
                  </button>
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Right Column - Summary */}
          <div className="interview-summary-section">
            <div className="interview-summary-sticky">
              <Card variant="elevated" padding="lg">
                <CardHeader>
                  <h2>Interview Summary</h2>
                </CardHeader>
                <CardBody>
                  <div className="interview-summary-item">
                    <span>Type</span>
                    <span className="interview-summary-value">
                      {config.interview_type.charAt(0).toUpperCase() + config.interview_type.slice(1)}
                    </span>
                  </div>
                  <div className="interview-summary-item">
                    <span>Position</span>
                    <span className="interview-summary-value">
                      {config.target_position || '(not specified)'}
                    </span>
                  </div>
                  <div className="interview-summary-item">
                    <span>Difficulty</span>
                    <Badge variant={getDifficultyBadgeVariant(config.difficulty_level)}>
                      {config.difficulty_level.charAt(0).toUpperCase() + config.difficulty_level.slice(1)}
                    </Badge>
                  </div>
                  <div className="interview-summary-item">
                    <span>Duration</span>
                    <span className="interview-summary-value">{config.duration_minutes} minutes</span>
                  </div>
                  <div className="interview-summary-item">
                    <span>Questions</span>
                    <span className="interview-summary-value">{config.question_count}</span>
                  </div>

                  <Button
                    variant="primary"
                    size="lg"
                    icon={<Zap size={20} />}
                    onClick={handleStart}
                    disabled={!canStart || !isResumeReady}
                    fullWidth
                    className="interview-summary-btn"
                  >
                    {loading ? 'Starting Interview...' : 'Start Interview'}
                  </Button>

                  {!isResumeReady && config.resume_id && (
                    <p className="interview-summary-notice" style={{ color: '#ff9800', fontWeight: 500 }}>
                      ⚠ Selected resume must be extracted before starting interview
                    </p>
                  )}

                  <p className="interview-summary-notice">
                    Your answers will be evaluated by AI and stored securely.
                  </p>
                </CardBody>
              </Card>
            </div>
          </div>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

InterviewSetup.displayName = 'InterviewSetup'