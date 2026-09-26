import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Upload,
  FileText,
  Check,
  Trash2,
  Eye,
  Plus,
  AlertCircle,
  Clock,
  X,
  Loader2,
} from 'lucide-react'
import { AppShell, AppShellContent, AppShellHeader } from '@/components/layout'
import { Button } from '@/components/Button'
import { Card, CardHeader, CardBody, CardFooter } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { Progress } from '@/components/Progress'
import { mockResumes } from '@/data/mockData'
import './Resumes.css'

type UploadStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error'

const fileTypeIcons: Record<string, string> = {
  pdf: '📄',
  doc: '📝',
  docx: '📝',
  txt: '📃',
  rtf: '📄',
  odt: '📄',
  html: '🌐',
  md: '📋',
}

export const Resumes: React.FC = () => {
  const [uploads, setUploads] = useState<Record<string, UploadStatus>>({})
  const [dragActive, setDragActive] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const resumes = mockResumes

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const files = e.dataTransfer.files
    if (files && files[0]) {
      simulateUpload(files[0].name)
    }
  }

  const simulateUpload = (filename: string) => {
    const id = `resume_${Date.now()}`
    setUploads((prev) => ({ ...prev, [id]: 'uploading' }))
    
    setTimeout(() => {
      setUploads((prev) => ({ ...prev, [id]: 'processing' }))
      setTimeout(() => {
        setUploads((prev) => ({ ...prev, [id]: 'completed' }))
      }, 2000)
    }, 1500)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      simulateUpload(files[0].name)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getUploadProgress = (status: UploadStatus): number => {
    switch (status) {
      case 'uploading': return 50
      case 'processing': return 75
      case 'completed': return 100
      default: return 0
    }
  }

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Resumes' },
      ]}
    >
      <AppShellContent maxWidth="full">
        {/* Page Header */}
        <div className="resumes-page-header">
          <div className="resumes-header-content">
            <h1>Resume Management</h1>
            <p>Upload and manage your resumes for AI-powered interviews</p>
          </div>
          <label className="resumes-upload-btn">
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt,.rtf,.odt,.html,.md"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            <Button variant="primary" size="lg" icon={<Plus size={20} />}>
              Upload Resume
            </Button>
          </label>
        </div>

        {/* Upload Area */}
        <Card variant="default" padding="lg" className="resumes-upload-card">
          <CardBody>
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`resumes-dropzone ${dragActive ? 'active' : ''}`}
            >
              <Upload className="resumes-dropzone-icon" />
              <h3>Drag and drop your resume</h3>
              <p>or click to browse files</p>
              <div className="resumes-file-types">
                {['PDF', 'DOC', 'DOCX', 'TXT', 'RTF', 'ODT', 'HTML', 'MD'].map((ext) => (
                  <Badge key={ext} variant="neutral" size="sm">{ext}</Badge>
                ))}
              </div>
              <span className="resumes-file-size">Maximum file size: 10MB</span>
            </div>

            {/* Upload Progress */}
            {Object.entries(uploads).map(([id, status]) => (
              <div key={id} className="resumes-upload-progress">
                <div className="resumes-progress-header">
                  <span>Uploading resume...</span>
                  {status === 'uploading' && <Loader2 className="resumes-spinner" size={16} />}
                  {status === 'processing' && <Badge variant="warning">Processing</Badge>}
                  {status === 'completed' && <Badge variant="success">Completed</Badge>}
                </div>
                <Progress 
                  value={getUploadProgress(status)} 
                  color={status === 'completed' ? 'success' : 'primary'}
                />
              </div>
            ))}
          </CardBody>
        </Card>

        {/* Resume List */}
        {resumes.length === 0 ? (
          <div className="resumes-empty">
            <FileText size={64} />
            <h3>No resumes yet</h3>
            <p>Upload your first resume to get started with AI-powered interviews</p>
            <Button variant="primary">Upload Resume</Button>
          </div>
        ) : (
          <div className="resumes-grid">
            {resumes.map((resume) => (
              <Card 
                key={resume.id} 
                variant="elevated" 
                padding="lg" 
                className={resume.isPrimary ? 'resumes-card-primary' : ''}
              >
                <CardBody>
                  <div className="resumes-card-header">
                    <div className="resumes-file-info">
                      <span className="resumes-file-icon">{fileTypeIcons[resume.fileType] || '📄'}</span>
                      <div>
                        <h3>{resume.filename}</h3>
                        <p>{formatFileSize(resume.fileSize)} • {formatDate(resume.uploadedDate)}</p>
                      </div>
                    </div>
                    {resume.isPrimary && <Badge variant="primary">Primary</Badge>}
                  </div>

                  {/* Status Badges */}
                  <div className="resumes-status-badges">
                    <Badge variant={resume.processingStatus === 'completed' ? 'success' : 'warning'}>
                      {resume.processingStatus === 'completed' ? <Check size={12} /> : <Clock size={12} />}
                      Processing: {resume.processingStatus}
                    </Badge>
                    <Badge variant={resume.analysisStatus === 'completed' ? 'success' : 'neutral'}>
                      Analysis: {resume.analysisStatus}
                    </Badge>
                  </div>

                  {/* Actions */}
                  <div className="resumes-card-actions">
                    <Link to={`/resumes/${resume.id}/analysis`} className="resumes-action-link">
                      <Button variant="primary" size="sm" icon={<Eye size={16} />}>
                        View Analysis
                      </Button>
                    </Link>
                    <Button variant="ghost" size="sm" icon={<Trash2 size={16} />}>
                      Delete
                    </Button>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}

        {/* Demo Notice */}
        <div className="resumes-demo-notice">
          <AlertCircle size={20} />
          <div>
            <p className="resumes-notice-title">Demo Data Notice</p>
            <p className="resumes-notice-text">
              This page shows mock resumes for demonstration. Upload functionality is simulated.
              Real file upload will be connected to backend API.
            </p>
          </div>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Resumes.displayName = 'Resumes'