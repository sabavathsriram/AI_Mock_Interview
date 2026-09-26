import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Zap,
  Clock,
  FileText,
  Target,
  BarChart2,
  Play,
  Check,
} from 'lucide-react'
import { AppShell, AppShellContent, AppShellHeader } from '@/components/layout'
import { Button } from '@/components/Button'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Tabs, TabsContent } from '@/components/common/Tabs'
import { mockResumes } from '@/data/mockData'
import './InterviewSetup.css'

const interviewTypes = [
  { value: 'technical', label: 'Technical', desc: 'Core CS, data structures, algorithms' },
  { value: 'hr', label: 'HR / Behavioral', desc: 'Past experiences, situational questions' },
  { value: 'behavioral', label: 'Behavioral', desc: 'Soft skills, leadership scenarios' },
  { value: 'system_design', label: 'System Design', desc: 'Scalable system architecture' },
  { value: 'coding', label: 'Coding', desc: 'Live coding challenges' },
  { value: 'mixed', label: 'Mixed', desc: 'Combination of all types' },
]

const difficulties = ['Easy', 'Medium', 'Hard', 'Adaptive']
const durations = [15, 30, 45, 60]
const modes = [
  { value: 'text', label: 'Text', icon: '💬' },
  { value: 'voice', label: 'Voice', icon: '🎤' },
  { value: 'video', label: 'Video', icon: '📹' },
]

const personalizationOptions = [
  { id: 'resume', label: 'Resume-based', desc: 'Questions tailored to your experience', icon: <FileText size={18} /> },
  { id: 'job', label: 'Job-description-based', desc: 'Match target job requirements', icon: <Target size={18} /> },
  { id: 'skills', label: 'Skill-gap-based', desc: 'Focus on weak areas', icon: <BarChart2 size={18} /> },
  { id: 'performance', label: 'Previous-performance', desc: 'Build on past interview data', icon: <Zap size={18} /> },
]

export const InterviewSetup: React.FC = () => {
  const navigate = useNavigate()
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [config, setConfig] = useState({
    type: 'technical',
    difficulty: 'Medium',
    duration: 30,
    mode: 'text',
    personalization: [] as string[],
  })

  const resumes = mockResumes
  const estimatedQuestions = Math.floor(config.duration / 5)

  const togglePersonalization = (id: string) => {
    setConfig((prev) => ({
      ...prev,
      personalization: prev.personalization.includes(id)
        ? prev.personalization.filter((p) => p !== id)
        : [...prev.personalization, id],
    }))
  }

  const canStart = config.type && config.difficulty && config.duration && config.mode

  const handleStart = () => {
    navigate('/interview/demo-session')
  }

  const getDifficultyBadgeVariant = (diff: string): 'success' | 'warning' | 'error' | 'primary' => {
    if (diff === 'Easy') return 'success'
    if (diff === 'Hard') return 'error'
    if (diff === 'Adaptive') return 'primary'
    return 'warning'
  }

  const difficultyDescriptions: Record<string, string> = {
    'Adaptive': 'Questions adapt based on your performance in real-time',
    'Easy': 'Fixed easy difficulty throughout the interview',
    'Medium': 'Fixed medium difficulty throughout the interview',
    'Hard': 'Fixed hard difficulty throughout the interview',
  }

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Mock Interview', href: '/interview/setup' },
      ]}
    >
      <AppShellContent maxWidth="full">
        {/* Page Header */}
        <div className="interview-page-header">
          <div className="interview-header-content">
            <h1>Setup Your Interview</h1>
            <p>Configure your mock interview parameters</p>
          </div>
          <Button
            variant="primary"
            size="lg"
            icon={<Play size={20} />}
            onClick={handleStart}
            disabled={!canStart}
          >
            Start AI Interview
          </Button>
        </div>

        <div className="interview-main-grid">
          {/* Left Column - Configuration */}
          <div className="interview-config-section">
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
                      onClick={() => setConfig((prev) => ({ ...prev, type: type.value }))}
                      className={`interview-type-card ${config.type === type.value ? 'selected' : ''}`}
                    >
                      <div className="interview-type-header">
                        <span className="interview-type-label">{type.label}</span>
                        {config.type === type.value && (
                          <Check size={18} className="interview-type-check" />
                        )}
                      </div>
                      <p className="interview-type-desc">{type.desc}</p>
                    </button>
                  ))}
                </div>
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
                      onClick={() => setConfig((prev) => ({ ...prev, difficulty: diff }))}
                      className={`interview-difficulty-btn ${config.difficulty === diff} ${diff.toLowerCase()}`}
                    >
                      {diff}
                    </button>
                  ))}
                </div>
                <p className="interview-difficulty-desc">
                  {difficultyDescriptions[config.difficulty]}
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
                      onClick={() => setConfig((prev) => ({ ...prev, duration: dur }))}
                      className={`interview-duration-card ${config.duration === dur ? 'selected' : ''}`}
                    >
                      <span className="interview-duration-value">{dur}</span>
                      <span className="interview-duration-label">min</span>
                    </button>
                  ))}
                </div>
                <p className="interview-duration-estimate">
                  Estimated: ~{estimatedQuestions} questions
                </p>
              </CardBody>
            </Card>

            {/* Mode */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Interview Mode</h2>
              </CardHeader>
              <CardBody>
                <div className="interview-mode-grid">
                  {modes.map((mode) => (
                    <button
                      key={mode.value}
                      onClick={() => setConfig((prev) => ({ ...prev, mode: mode.value }))}
                      className={`interview-mode-card ${config.mode === mode.value ? 'selected' : ''}`}
                    >
                      <span className="interview-mode-icon">{mode.icon}</span>
                      <span className="interview-mode-label">{mode.label}</span>
                      {(mode.value === 'voice' || mode.value === 'video') && (
                        <Badge variant="warning" size="sm" className="interview-mode-badge">Coming Soon</Badge>
                      )}
                    </button>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Personalization */}
            <Card variant="default" padding="lg">
              <CardHeader>
                <h2>Personalization</h2>
                <p>How should the AI tailor the interview?</p>
              </CardHeader>
              <CardBody>
                <div className="interview-personalization-list">
                  {personalizationOptions.map((option) => (
                    <button
                      key={option.id}
                      onClick={() => togglePersonalization(option.id)}
                      className={`interview-personalization-card ${config.personalization.includes(option.id) ? 'selected' : ''}`}
                    >
                      <div className="interview-personalization-icon">{option.icon}</div>
                      <div className="interview-personalization-content">
                        <span className="interview-personalization-label">{option.label}</span>
                        <p className="interview-personalization-desc">{option.desc}</p>
                      </div>
                      {config.personalization.includes(option.id) && (
                        <Check size={20} className="interview-personalization-check" />
                      )}
                    </button>
                  ))}
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
                      {interviewTypes.find((t) => t.value === config.type)?.label}
                    </span>
                  </div>
                  <div className="interview-summary-item">
                    <span>Difficulty</span>
                    <Badge variant={getDifficultyBadgeVariant(config.difficulty)}>
                      {config.difficulty}
                    </Badge>
                  </div>
                  <div className="interview-summary-item">
                    <span>Duration</span>
                    <span className="interview-summary-value">{config.duration} minutes</span>
                  </div>
                  <div className="interview-summary-item">
                    <span>Mode</span>
                    <span className="interview-summary-value capitalize">{config.mode}</span>
                  </div>
                  <div className="interview-summary-item">
                    <span>Questions</span>
                    <span className="interview-summary-value">~{estimatedQuestions}</span>
                  </div>

                  {config.personalization.length > 0 && (
                    <div className="interview-summary-personalization">
                      <span>Personalization</span>
                      <div className="interview-summary-badges">
                        {config.personalization.map((p) => (
                          <Badge key={p} variant="neutral" size="sm">
                            {personalizationOptions.find((o) => o.id === p)?.label}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    variant="primary"
                    size="lg"
                    icon={<Zap size={20} />}
                    onClick={handleStart}
                    disabled={!canStart}
                    fullWidth
                    className="interview-summary-btn"
                  >
                    Start AI Interview
                  </Button>

                  <p className="interview-summary-notice">
                    This is a demo interview with mock data
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