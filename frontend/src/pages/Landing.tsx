import React from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Brain,
  BarChart3,
  BookOpen,
  Zap,
  Shield,
  Github,
  Linkedin,
  Twitter,
  Check,
} from 'lucide-react'
import { Button } from '@/components/common'
import './Landing.css'

export const Landing: React.FC = () => {
  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-container">
          <Link to="/" className="nav-logo">
            <div className="logo-mark">AI</div>
            <span className="logo-text">MockInterview</span>
          </Link>

          <div className="nav-actions">
            <Link to="/login" className="btn-link">
              Sign In
            </Link>
            <Link to="/register">
              <Button variant="primary" size="sm">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-bg-decoration">
          <div className="hero-gradient hero-gradient-1"></div>
          <div className="hero-gradient hero-gradient-2"></div>
        </div>

        <div className="section-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Master Your <span className="gradient-text">Interview Skills</span>
            </h1>

            <p className="hero-subtitle">
              Practice with AI-powered interviewers, get real-time feedback, and land your dream job with personalized learning roadmaps.
            </p>

            <div className="hero-actions">
              <Link to="/interview/setup">
                <Button variant="primary" size="lg" className="btn-with-icon">
                  Start Mock Interview
                  <ArrowRight size={20} />
                </Button>
              </Link>
              <Link to="/resumes">
                <Button variant="secondary" size="lg">
                  Upload Resume
                </Button>
              </Link>
            </div>

            {/* Demo indicator */}
            <div className="demo-badge">
              <span className="demo-indicator"></span>
              <span>Demo data - Replace with real API integration</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-container">
          <div className="section-header">
            <h2>Powerful Features for Interview Success</h2>
            <p>Everything you need to prepare for your next technical interview</p>
          </div>

          <div className="features-grid">
            {[
              {
                icon: <Brain size={24} />,
                title: 'AI-Powered Questions',
                description: 'Adaptive questions that adjust to your skill level and experience',
              },
              {
                icon: <BarChart3 size={24} />,
                title: 'Real-Time Feedback',
                description: 'Get instant performance analysis on every answer',
              },
              {
                icon: <Zap size={24} />,
                title: 'Skill Gap Analysis',
                description: 'Identify exactly what to improve with detailed reports',
              },
              {
                icon: <BookOpen size={24} />,
                title: 'Learning Roadmap',
                description: 'Personalized learning paths based on your weaknesses',
              },
              {
                icon: <BarChart3 size={24} />,
                title: 'Progress Tracking',
                description: 'Watch your improvement across multiple interview attempts',
              },
              {
                icon: <Shield size={24} />,
                title: 'Privacy Focused',
                description: 'Your data is secure and never shared with third parties',
              },
            ].map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works">
        <div className="section-container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>6 simple steps to interview mastery</p>
          </div>

          <div className="how-it-works-grid">
            {[
              { num: 1, title: 'Upload Your Resume', desc: 'Share your background so AI understands your profile' },
              { num: 2, title: 'AI Analyzes Your Profile', desc: 'Advanced NLP extracts skills, experience, and expertise' },
              { num: 3, title: 'Start Adaptive Interview', desc: 'Answer AI-generated questions tailored to your level' },
              { num: 4, title: 'Get Real-Time Feedback', desc: 'Receive detailed evaluation on technical and soft skills' },
              { num: 5, title: 'Identify Skill Gaps', desc: 'See exact areas where you need improvement' },
              { num: 6, title: 'Follow Learning Path', desc: 'Get curated resources and practice problems' },
            ].map((step) => (
              <div key={step.num} className="how-it-works-card">
                <div className="step-number">{step.num}</div>
                <h3>{step.title}</h3>
                <p>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="tech-stack-section">
        <div className="section-container">
          <div className="section-header">
            <h2>Built with Enterprise-Grade Technology</h2>
            <p>Leveraging cutting-edge AI and cloud infrastructure</p>
          </div>

          <div className="tech-grid">
            {[
              { title: 'LLMs', desc: 'Google Gemini for intelligent question generation' },
              { title: 'RAG', desc: 'Retrieval-Augmented Generation for contextual answers' },
              { title: 'Vector DB', desc: 'ChromaDB for semantic search and embeddings' },
              { title: 'Multi-Agent', desc: 'Orchestrated agents for different interview types' },
              { title: 'Resume AI', desc: 'Advanced document parsing and skill extraction' },
              { title: 'Adaptive', desc: 'Dynamic difficulty adjustment based on performance' },
              { title: 'Real-time', desc: 'Instant feedback and evaluation' },
              { title: 'Scalable', desc: 'Cloud-native architecture for reliability' },
            ].map((tech, index) => (
              <div key={index} className="tech-card">
                <h3>{tech.title}</h3>
                <p>{tech.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Statistics */}
      <section className="statistics-section">
        <div className="section-container">
          <div className="stats-grid">
            {[
              { label: 'Users', value: '10K+' },
              { label: 'Interviews', value: '100K+' },
              { label: 'Success Rate', value: '94%' },
              { label: 'Avg. Score Improvement', value: '+18%' },
            ].map((stat, index) => (
              <div key={index} className="stat-card">
                <div className="stat-value">{stat.value}</div>
                <p className="stat-label">{stat.label}</p>
              </div>
            ))}
          </div>

          <div className="demo-notice">
            <p>
              ⚠️ <strong>Demo Data Notice:</strong> Statistics above are for demonstration purposes only
            </p>
            <p className="demo-notice-subtitle">
              Real statistics will be populated once you complete interviews
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section">
        <div className="section-container">
          <div className="section-header">
            <h2>Simple, Transparent Pricing</h2>
            <p>Perfect for students and professionals</p>
          </div>

          <div className="pricing-grid">
            {[
              {
                name: 'Free',
                price: '$0',
                desc: 'Perfect to get started',
                features: [
                  'Unlimited mock interviews',
                  'Basic performance analytics',
                  'Resume upload (1)',
                  'Community resources',
                ],
              },
              {
                name: 'Pro',
                price: '$9.99',
                period: '/month',
                desc: 'Most popular',
                featured: true,
                features: [
                  'Everything in Free, plus:',
                  'Advanced skill analysis',
                  '5 resume uploads',
                  'AI-powered feedback',
                  'Personalized learning paths',
                ],
              },
              {
                name: 'Premium',
                price: '$19.99',
                period: '/month',
                desc: 'For serious learners',
                features: [
                  'Everything in Pro, plus:',
                  'Video interview practice',
                  'Unlimited resume uploads',
                  'Priority support',
                  'Custom interview templates',
                ],
              },
            ].map((plan, index) => (
              <div
                key={index}
                className={`pricing-card ${plan.featured ? 'pricing-card-featured' : ''}`}
              >
                <h3 className="pricing-card-title">{plan.name}</h3>
                <p className="pricing-card-desc">{plan.desc}</p>
                <div className="pricing-card-price">
                  <span>{plan.price}</span>
                  {plan.period && <span className="pricing-period">{plan.period}</span>}
                </div>
                <Button
                  variant={plan.featured ? 'secondary' : 'primary'}
                  fullWidth
                  className="pricing-card-btn"
                >
                  Get Started
                </Button>
                <ul className="pricing-features">
                  {plan.features.map((feature, i) => (
                    <li key={i}>
                      <Check size={20} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="section-container">
          <div className="cta-content">
            <h2>Ready to Master Your Interviews?</h2>
            <p>Join thousands of candidates who have improved their interview skills</p>
            <div className="cta-actions">
              <Link to="/register">
                <Button variant="secondary" size="lg" className="btn-with-icon">
                  Start Free Today
                  <ArrowRight size={20} />
                </Button>
              </Link>
              <Link to="/interview/setup">
                <Button variant="secondary" size="lg">
                  Try Demo Interview
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="section-container">
          <div className="footer-content">
            <div className="footer-column">
              <Link to="/" className="nav-logo">
                <div className="logo-mark">AI</div>
                <span className="logo-text">MockInterview</span>
              </Link>
              <p>Master your interview skills with AI-powered practice</p>
            </div>

            {[
              { title: 'Product', links: ['Features', 'Pricing', 'Security'] },
              { title: 'Company', links: ['About', 'Blog', 'Contact'] },
              { title: 'Resources', links: ['Docs', 'FAQ', 'Support'] },
            ].map((col, index) => (
              <div key={index} className="footer-column">
                <h4>{col.title}</h4>
                <ul>
                  {col.links.map((link) => (
                    <li key={link}>
                      <a href="#">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="footer-bottom">
            <p>© 2024 AI Mock Interview System. All rights reserved.</p>

            <div className="social-links">
              {[
                { icon: Github, href: '#' },
                { icon: Linkedin, href: '#' },
                { icon: Twitter, href: '#' },
              ].map((social, index) => {
                const Icon = social.icon
                return (
                  <a key={index} href={social.href} className="social-link">
                    <Icon size={18} />
                  </a>
                )
              })}
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

Landing.displayName = 'Landing'
