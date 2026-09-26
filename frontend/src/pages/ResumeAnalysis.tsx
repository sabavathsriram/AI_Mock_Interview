import React from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  GraduationCap,
  Award,
  Code,
  Database,
  Cloud,
  Wrench,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Button } from '@/components/common'
import { mockResumeAnalysis } from '@/data/mockData'
import './ResumeAnalysis.css'

const skillCategories = [
  { name: 'Programming Languages', icon: <Code size={18} />, skills: mockResumeAnalysis.skills.programming },
  { name: 'Frameworks', icon: <Code size={18} />, skills: mockResumeAnalysis.skills.frameworks },
  { name: 'Databases', icon: <Database size={18} />, skills: mockResumeAnalysis.skills.databases },
  { name: 'Cloud & DevOps', icon: <Cloud size={18} />, skills: mockResumeAnalysis.skills.cloud },
  { name: 'Tools', icon: <Wrench size={18} />, skills: mockResumeAnalysis.skills.tools },
]

const evidenceItems = [
  { skill: 'Python', evidence: 'Developed Flask backend APIs, data processing pipelines, automation scripts', confidence: 94 },
  { skill: 'React', evidence: 'Built responsive UI components, state management, frontend architecture', confidence: 87 },
  { skill: 'System Design', evidence: 'Designed microservices, API gateways, distributed systems', confidence: 82 },
  { skill: 'AWS', evidence: 'EC2, S3, Lambda, CloudFormation, deployment pipelines', confidence: 78 },
  { skill: 'PostgreSQL', evidence: 'Complex queries, migrations, performance optimization', confidence: 91 },
]

export const ResumeAnalysis: React.FC = () => {
  const { id } = useParams()
  const analysis = mockResumeAnalysis
  const [isDarkMode, setIsDarkMode] = React.useState(false)

  const getConfidenceVariant = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 90) return 'success'
    if (confidence >= 80) return 'warning'
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

          {/* Header */}
          <div className="resume-analysis-header">
            <div className="resume-analysis-header-content">
              <h1>Resume Intelligence Analysis</h1>
              <p>AI-powered analysis of your resume</p>
            </div>
          </div>

          {/* Candidate Overview */}
          <Card variant="elevated" padding="lg" className="resume-analysis-overview">
            <CardHeader>
              <div className="resume-analysis-overview-header">
                <Briefcase size={20} />
                <h2>Candidate Overview</h2>
              </div>
            </CardHeader>
            <CardBody>
              <div className="resume-analysis-overview-grid">
                <div className="resume-analysis-overview-left">
                  <h3>{analysis.candidateOverview.fullName}</h3>
                  <p className="resume-analysis-headline">{analysis.candidateOverview.headline}</p>
                  <p className="resume-analysis-summary">{analysis.candidateOverview.summary}</p>
                  <div className="resume-analysis-contact">
                    <div className="resume-analysis-contact-item">
                      <Mail size={16} />
                      <span>{analysis.candidateOverview.email}</span>
                    </div>
                    <div className="resume-analysis-contact-item">
                      <Phone size={16} />
                      <span>{analysis.candidateOverview.phone}</span>
                    </div>
                    <div className="resume-analysis-contact-item">
                      <MapPin size={16} />
                      <span>{analysis.candidateOverview.location}</span>
                    </div>
                  </div>
                </div>
                <div className="resume-analysis-overview-right">
                  <div className="resume-analysis-domains">
                    <h4>Primary Domains</h4>
                    <div className="resume-analysis-badges">
                      {analysis.primaryDomains.map((domain) => (
                        <Badge key={domain} variant="primary" size="sm">{domain}</Badge>
                      ))}
                    </div>
                  </div>
                  <div className="resume-analysis-domains">
                    <h4>Secondary Domains</h4>
                    <div className="resume-analysis-badges">
                      {analysis.secondaryDomains.map((domain) => (
                        <Badge key={domain} variant="secondary" size="sm">{domain}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Education */}
          <Card variant="default" padding="lg" className="resume-analysis-section">
            <CardHeader>
              <div className="resume-analysis-section-header">
                <GraduationCap size={20} />
                <h2>Education</h2>
              </div>
            </CardHeader>
            <CardBody>
              <div className="resume-analysis-education-list">
                {analysis.education.map((edu, index) => (
                  <div key={index} className="resume-analysis-education-item">
                    <div className="resume-analysis-education-main">
                      <h4>{edu.degree} in {edu.field}</h4>
                      <p>{edu.institution}</p>
                    </div>
                    <div className="resume-analysis-education-meta">
                      <span className="resume-analysis-year">{edu.graduationYear}</span>
                      <span className="resume-analysis-gpa">GPA: {edu.gpa}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Experience */}
          <Card variant="default" padding="lg" className="resume-analysis-section">
            <CardHeader>
              <div className="resume-analysis-section-header">
                <Briefcase size={20} />
                <h2>Experience</h2>
              </div>
            </CardHeader>
            <CardBody>
              <div className="resume-analysis-experience-list">
                {analysis.experience.map((exp, index) => (
                  <div key={index} className="resume-analysis-experience-item">
                    <div className="resume-analysis-experience-header">
                      <div className="resume-analysis-experience-title">
                        <h4>{exp.title}</h4>
                        <p>{exp.company}</p>
                      </div>
                      <Badge variant="neutral" size="sm">{exp.duration}</Badge>
                    </div>
                    <p className="resume-analysis-experience-description">{exp.description}</p>
                    <div className="resume-analysis-achievements">
                      {exp.achievements.map((achievement, i) => (
                        <div key={i} className="resume-analysis-achievement">
                          <CheckCircle size={14} />
                          <span>{achievement}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Technical Skills */}
          <Card variant="default" padding="lg" className="resume-analysis-section">
            <CardHeader>
              <h2>Technical Skills</h2>
            </CardHeader>
            <CardBody>
              <div className="resume-analysis-skills-grid">
                {skillCategories.map((category) => (
                  <div key={category.name} className="resume-analysis-skill-category">
                    <h4>
                      {category.icon}
                      {category.name}
                    </h4>
                    <div className="resume-analysis-skill-tags">
                      {category.skills.map((skill) => (
                        <Badge key={skill} variant="primary" size="sm">{skill}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Certifications */}
          <Card variant="default" padding="lg" className="resume-analysis-section">
            <CardHeader>
              <div className="resume-analysis-section-header">
                <Award size={20} />
                <h2>Certifications</h2>
              </div>
            </CardHeader>
            <CardBody>
              <div className="resume-analysis-certifications-list">
                {analysis.certifications.map((cert, index) => (
                  <div key={index} className="resume-analysis-certification-item">
                    <div className="resume-analysis-certification-main">
                      <h4>{cert.name}</h4>
                      <p>{cert.issuer}</p>
                    </div>
                    <div className="resume-analysis-certification-dates">
                      <span>Issued: {new Date(cert.issuedDate).toLocaleDateString()}</span>
                      {cert.expiryDate && (
                        <span>Expires: {new Date(cert.expiryDate).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Resume Evidence */}
          <Card variant="default" padding="lg" className="resume-analysis-section">
            <CardHeader>
              <div className="resume-analysis-section-header">
                <CheckCircle size={20} />
                <h2>Resume Evidence</h2>
              </div>
            </CardHeader>
            <CardBody>
              <p className="resume-analysis-section-description">
                AI-detected skills with evidence from your resume and confidence scores
              </p>
              <div className="resume-analysis-evidence-list">
                {evidenceItems.map((item, index) => (
                  <div key={index} className="resume-analysis-evidence-item">
                    <div className="resume-analysis-evidence-header">
                      <h4>{item.skill}</h4>
                      <Badge variant={getConfidenceVariant(item.confidence)} size="sm">
                        {item.confidence}%
                      </Badge>
                    </div>
                    <p className="resume-analysis-evidence-text">"{item.evidence}"</p>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Strengths & Gaps */}
          <div className="resume-analysis-assessment-grid">
            <Card variant="default" padding="lg" className="resume-analysis-strengths">
              <CardHeader>
                <div className="resume-analysis-assessment-header strengths">
                  <CheckCircle size={20} />
                  <h2>Resume Strengths</h2>
                </div>
              </CardHeader>
              <CardBody>
                <ul className="resume-analysis-assessment-list">
                  {analysis.strengths.map((strength, index) => (
                    <li key={index} className="resume-analysis-assessment-item">
                      <CheckCircle size={16} />
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </CardBody>
            </Card>

            <Card variant="default" padding="lg" className="resume-analysis-gaps">
              <CardHeader>
                <div className="resume-analysis-assessment-header gaps">
                  <AlertTriangle size={20} />
                  <h2>Potential Skill Gaps</h2>
                </div>
              </CardHeader>
              <CardBody>
                <ul className="resume-analysis-assessment-list">
                  {analysis.skillGaps.map((gap, index) => (
                    <li key={index} className="resume-analysis-assessment-item">
                      <AlertTriangle size={16} />
                      <span>{gap}</span>
                    </li>
                  ))}
                </ul>
              </CardBody>
            </Card>
          </div>

          {/* Demo Notice */}
          <Card variant="default" padding="md" className="resume-analysis-demo-notice">
            <CardBody>
              <p>📊 <strong>Demo Data:</strong> This analysis is based on mock data. Real analysis will be generated by the Resume Intelligence backend.</p>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

ResumeAnalysis.displayName = 'ResumeAnalysis'
