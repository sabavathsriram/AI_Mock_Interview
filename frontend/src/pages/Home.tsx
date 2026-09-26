import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Brain, BarChart3, Zap, ArrowRight } from 'lucide-react'
import { AppShell } from '@/components/layout'
import { Button } from '@/components/common'
import './Home.css'

const Home: React.FC = () => {
  const navigate = useNavigate()

  const handleStartInterview = () => {
    navigate('/interview/setup')
  }

  const handleUploadResume = () => {
    navigate('/resumes')
  }

  return (
    <AppShell>
      <div className="home-page">
        {/* Hero Section */}
        <section className="home-hero">
          <div className="hero-container">
            <div className="hero-content">
              <h1 className="hero-title">
                Master Your <span className="gradient-text">Interview Skills</span>
              </h1>
              <p className="hero-subtitle">
                Practice with AI-powered interviewers, get real-time feedback, and land your dream job with personalized learning paths.
              </p>
              
              <div className="hero-actions">
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={handleStartInterview}
                  className="btn-with-icon"
                >
                  Start Mock Interview
                  <ArrowRight size={20} />
                </Button>
                <Button 
                  variant="secondary" 
                  size="lg"
                  onClick={handleUploadResume}
                >
                  Upload Resume
                </Button>
              </div>
            </div>

            <div className="hero-stats">
              <div className="stat">
                <div className="stat-value">100K+</div>
                <div className="stat-label">Interviews Completed</div>
              </div>
              <div className="stat">
                <div className="stat-value">94%</div>
                <div className="stat-label">Success Rate</div>
              </div>
              <div className="stat">
                <div className="stat-value">+18%</div>
                <div className="stat-label">Avg. Score Improvement</div>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Start Section */}
        <section className="home-quick-start">
          <div className="quick-start-container">
            <h2>Get Started in 3 Steps</h2>
            <div className="quick-start-grid">
              <div className="quick-start-card">
                <div className="quick-start-icon">1</div>
                <h3>Select a Role</h3>
                <p>Choose your target position and experience level</p>
              </div>
              <div className="quick-start-card">
                <div className="quick-start-icon">2</div>
                <h3>Answer Questions</h3>
                <p>Practice with AI-generated interview questions</p>
              </div>
              <div className="quick-start-card">
                <div className="quick-start-icon">3</div>
                <h3>Get Feedback</h3>
                <p>Receive instant analysis and improvement tips</p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="home-features">
          <div className="features-container">
            <h2>Why Choose MockInterview?</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">
                  <Brain size={24} />
                </div>
                <h3>AI-Powered Questions</h3>
                <p>Smart questions adapted to your experience level and target role</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">
                  <BarChart3 size={24} />
                </div>
                <h3>Real-Time Feedback</h3>
                <p>Get instant feedback on your answers and communication skills</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">
                  <Zap size={24} />
                </div>
                <h3>Performance Tracking</h3>
                <p>Track your progress and identify areas for improvement</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="home-cta">
          <div className="cta-container">
            <h2>Ready to Transform Your Interviews?</h2>
            <p>Join thousands of candidates who have improved their interview skills</p>
            <Button 
              variant="secondary" 
              size="lg"
              onClick={handleStartInterview}
              className="btn-with-icon"
            >
              Start Your First Interview
              <ArrowRight size={20} />
            </Button>
          </div>
        </section>
      </div>
    </AppShell>
  )
}

export default Home