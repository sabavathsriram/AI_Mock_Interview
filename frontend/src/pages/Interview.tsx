import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Send,
  SkipForward,
  Clock,
  Mic,
  MicOff,
  Volume2,
  ChevronDown,
  AlertCircle,
  CheckCircle,
  Zap,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { Card, CardBody } from '@/components/Card'
import { Badge } from '@/components/Badge'
import './Interview.css'

const mockQuestions = [
  {
    id: 1,
    question: "Can you explain the difference between a stack and a queue data structure? When would you use each one?",
    category: "Data Structures",
    difficulty: "Medium",
    expectedTime: 120,
  },
  {
    id: 2,
    question: "Describe the process of making an HTTP request. What happens from the moment you type a URL until the page loads?",
    category: "Computer Networks",
    difficulty: "Medium",
    expectedTime: 180,
  },
  {
    id: 3,
    question: "What is the time complexity of quick sort in the average and worst case? How can we optimize it?",
    category: "Algorithms",
    difficulty: "Hard",
    expectedTime: 150,
  },
  {
    id: 4,
    question: "Design a URL shortener service that can handle millions of requests. What are the key components and trade-offs?",
    category: "System Design",
    difficulty: "Hard",
    expectedTime: 300,
  },
]

type AIState = 'thinking' | 'asking' | 'listening' | 'evaluating' | 'generating'

export const Interview: React.FC = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answer, setAnswer] = useState('')
  const [timeLeft, setTimeLeft] = useState(120)
  const [isRecording, setIsRecording] = useState(false)
  const [aiState, setAiState] = useState<AIState>('asking')
  const [showReasoning, setShowReasoning] = useState(false)

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [timeLeft])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleSubmitAnswer = () => {
    if (!answer.trim()) return

    setAiState('evaluating')
    
    setTimeout(() => {
      setAiState('generating')
      setTimeout(() => {
        if (currentQuestion < mockQuestions.length - 1) {
          setShowReasoning(true)
          setTimeout(() => {
            setShowReasoning(false)
            setAiState('asking')
            setCurrentQuestion((prev) => prev + 1)
            setTimeLeft(mockQuestions[currentQuestion + 1].expectedTime)
            setAnswer('')
          }, 2500)
        } else {
          navigate(`/interview/${id || 'demo-session'}/results`)
        }
      }, 2000)
    }, 1500)
  }

  const handleSkip = () => {
    if (currentQuestion < mockQuestions.length - 1) {
      setCurrentQuestion((prev) => prev + 1)
      setTimeLeft(mockQuestions[currentQuestion + 1].expectedTime)
      setAnswer('')
    } else {
      navigate(`/interview/${id || 'demo-session'}/results`)
    }
  }

  const getAIStateIcon = () => {
    switch (aiState) {
      case 'evaluating':
        return '✓'
      case 'generating':
        return '⚡'
      case 'listening':
        return '🎤'
      default:
        return '🤖'
    }
  }

  const getAIStateText = () => {
    switch (aiState) {
      case 'thinking':
        return 'Analyzing your response...'
      case 'listening':
        return 'Listening to your answer...'
      case 'evaluating':
        return 'Evaluating your response...'
      case 'generating':
        return 'Generating next question...'
      default:
        return 'Ready for your answer'
    }
  }

  const timePercentage = (timeLeft / mockQuestions[currentQuestion].expectedTime) * 100
  const isTimeWarning = timeLeft < 30

  const getDifficultyVariant = (diff: string): 'success' | 'warning' | 'error' => {
    if (diff === 'Easy') return 'success'
    if (diff === 'Hard') return 'error'
    return 'warning'
  }

  return (
    <div className="interview-workspace">
      {/* Top Bar */}
      <div className="interview-topbar">
        <div className="interview-topbar-left">
          <div className="interview-topbar-logo">AI</div>
          <div className="interview-topbar-info">
            <span className="interview-topbar-title">Interview Session</span>
            <span className="interview-topbar-category">{mockQuestions[currentQuestion].category}</span>
          </div>
        </div>
        <div className="interview-topbar-middle">
          <div className={`interview-timer ${isTimeWarning ? 'warning' : ''}`}>
            <Clock size={20} />
            <span>{formatTime(timeLeft)}</span>
          </div>
        </div>
        <div className="interview-topbar-right">
          <span className="interview-question-counter">
            {currentQuestion + 1} / {mockQuestions.length}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="interview-progress-container">
        <div className="interview-progress-bar">
          {mockQuestions.map((_, index) => (
            <div
              key={index}
              className={`interview-progress-dot ${index < currentQuestion ? 'completed' : index === currentQuestion ? 'active' : 'pending'}`}
            />
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="interview-content">
        {/* Left - AI Interviewer */}
        <div className="interview-main">
          {/* AI Interviewer Card */}
          <div className="interview-ai-section">
            <div className="interview-ai-header">
              <div className="interview-ai-avatar">
                <span className="interview-avatar-icon">{getAIStateIcon()}</span>
                {aiState !== 'asking' && <div className="interview-avatar-pulse"></div>}
              </div>
              <div className="interview-ai-status">
                <h2>AI Interviewer</h2>
                <p className={`interview-status-text ${aiState !== 'asking' ? 'active' : ''}`}>
                  {getAIStateText()}
                </p>
              </div>
            </div>

            {/* Question Display */}
            <Card variant="elevated" padding="lg" className="interview-question-card">
              <CardBody>
                <p className="interview-question-text">
                  {mockQuestions[currentQuestion].question}
                </p>
                <div className="interview-question-meta">
                  <Badge variant={getDifficultyVariant(mockQuestions[currentQuestion].difficulty)}>
                    {mockQuestions[currentQuestion].difficulty}
                  </Badge>
                </div>
              </CardBody>
            </Card>

            {/* Reasoning Panel */}
            {showReasoning && (
              <Card variant="default" padding="md" className="interview-reasoning-card">
                <CardBody>
                  <div className="interview-reasoning-header">
                    <AlertCircle size={18} />
                    <span>AI Analysis</span>
                  </div>
                  <p className="interview-reasoning-text">
                    Your answer demonstrated strong understanding of core concepts. Proceeding to the next topic to explore your knowledge depth.
                  </p>
                </CardBody>
              </Card>
            )}

            {/* Answer Input */}
            <Card variant="default" padding="lg" className="interview-answer-card">
              <CardBody>
                <label className="interview-answer-label">Your Response</label>
                <textarea
                  className="interview-answer-textarea"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Share your thoughts here. Explain your reasoning step by step..."
                  disabled={aiState !== 'asking'}
                  rows={6}
                />
                
                {/* Input Controls */}
                <div className="interview-input-controls">
                  <div className="interview-voice-controls">
                    <button
                      className={`interview-voice-btn ${isRecording ? 'recording' : ''}`}
                      onClick={() => setIsRecording(!isRecording)}
                      title={isRecording ? 'Stop recording' : 'Start voice input'}
                    >
                      {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
                      <span>{isRecording ? 'Recording' : 'Voice'}</span>
                    </button>
                    <button className="interview-voice-btn" title="Play question aloud">
                      <Volume2 size={18} />
                      <span>Listen</span>
                    </button>
                  </div>

                  <div className="interview-submit-controls">
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={<SkipForward size={18} />}
                      onClick={handleSkip}
                      disabled={aiState !== 'asking'}
                    >
                      Skip
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      icon={<Send size={18} />}
                      onClick={handleSubmitAnswer}
                      disabled={!answer.trim() || aiState !== 'asking'}
                    >
                      Submit Answer
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        </div>

        {/* Right - Sidebar */}
        <div className="interview-sidebar">
          {/* Interview Stats */}
          <Card variant="default" padding="md">
            <CardBody>
              <h3 className="interview-sidebar-title">Interview Overview</h3>
              <div className="interview-stats-list">
                <div className="interview-stat-row">
                  <span>Type</span>
                  <span className="interview-stat-value">Technical</span>
                </div>
                <div className="interview-stat-row">
                  <span>Difficulty</span>
                  <Badge variant={getDifficultyVariant(mockQuestions[currentQuestion].difficulty)} size="sm">
                    {mockQuestions[currentQuestion].difficulty}
                  </Badge>
                </div>
                <div className="interview-stat-row">
                  <span>Questions</span>
                  <span className="interview-stat-value">{currentQuestion + 1} of {mockQuestions.length}</span>
                </div>
                <div className="interview-stat-row">
                  <span>Progress</span>
                  <span className="interview-stat-value">{Math.round((currentQuestion / mockQuestions.length) * 100)}%</span>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Time Progress */}
          <Card variant="default" padding="md">
            <CardBody>
              <h3 className="interview-sidebar-title">Time Remaining</h3>
              <div className="interview-time-progress">
                <div className="interview-progress-circle">
                  <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" className="interview-circle-bg" />
                    <circle 
                      cx="50" 
                      cy="50" 
                      r="45" 
                      className={`interview-circle-progress ${isTimeWarning ? 'warning' : ''}`}
                      style={{ 
                        strokeDasharray: `${282.7 * (timePercentage / 100)} 282.7`,
                        strokeDashoffset: 0
                      }}
                    />
                  </svg>
                  <div className="interview-time-display">{formatTime(timeLeft)}</div>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Adaptive Indicators */}
          <Card variant="default" padding="md">
            <CardBody>
              <h3 className="interview-sidebar-title">AI Adaptation</h3>
              <div className="interview-indicators-list">
                <div className="interview-indicator-item completed">
                  <CheckCircle size={16} />
                  <span>Previous answer evaluated</span>
                </div>
                <div className={`interview-indicator-item ${aiState === 'evaluating' ? 'active' : 'pending'}`}>
                  <Zap size={16} />
                  <span>Skill confidence updated</span>
                </div>
                <div className={`interview-indicator-item ${aiState === 'generating' ? 'active' : 'pending'}`}>
                  <Zap size={16} />
                  <span>Difficulty adjusted</span>
                </div>
                <div className="interview-indicator-item pending">
                  <ChevronDown size={16} />
                  <span>Next question generated</span>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* End Session */}
          <Button 
            variant="secondary" 
            fullWidth 
            onClick={() => navigate(`/interview/${id || 'demo-session'}/results`)}
          >
            End Session Early
          </Button>
        </div>
      </div>
    </div>
  )
}

Interview.displayName = 'Interview'