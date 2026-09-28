import React, { useState, useEffect } from 'react'
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
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/contexts/ThemeContext'
import { resumeService, type ResumeDetailResponse } from '@/services/api'
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
  const { user, logout } = useAuth()
  const { isDarkMode, toggleDarkMode } = useTheme()
  
  const [resumes, setResumes] = useState<ResumeDetailResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [uploads, setUploads] = useState<Record<string, { status: UploadStatus; error?: string; progress: number }>>({})
  const [dragActive, setDragActive] = useState(false)
  const [uploadingFileId, setUploadingFileId] = useState<string | null>(null)

  const userName = user?.full_name || 'User'
  const userEmail = user?.email || ''

  // Fetch resumes from backend
  const fetchResumes = async () => {
    try {
      setLoading(true)
      const response = await resumeService.listResumes()
      if (response.data.resumes) {
        setResumes(response.data.resumes)
      }
    } catch (error) {
      console.error('Error fetching resumes:', error)
      // Don't set empty array - keep existing resumes if fetch fails
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchResumes()
  }, [])

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
      handleFileUpload(files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    // Prevent duplicate uploads
    if (uploadingFileId) {
      console.warn('Upload already in progress')
      return
    }

    const uploadId = `resume_${Date.now()}`
    setUploadingFileId(uploadId)
    setUploads((prev) => ({ 
      ...prev, 
      [uploadId]: { status: 'uploading', progress: 0, error: undefined }
    }))
    
    try {
      // Validate file first
      const validation = await resumeService.validateFile(file)
      if (!validation.valid) {
        setUploads((prev) => ({ 
          ...prev, 
          [uploadId]: { status: 'error', progress: 0, error: validation.error }
        }))
        setUploadingFileId(null)
        return
      }

      // Upload the file with progress callback
      const response = await resumeService.uploadResume(
        file,
        undefined,
        false,
        (progress) => {
          // Update progress
          setUploads((prev) => ({
            ...prev,
            [uploadId]: { 
              status: 'uploading', 
              progress: progress.percentage,
              error: undefined
            }
          }))
        }
      )
      
      if (response.data) {
        // Update upload status to processing
        setUploads((prev) => ({ 
          ...prev, 
          [uploadId]: { status: 'processing', progress: 100, error: undefined }
        }))
        
        // Wait a moment then mark as completed
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        setUploads((prev) => ({ 
          ...prev, 
          [uploadId]: { status: 'completed', progress: 100, error: undefined }
        }))
        
        // Refresh resume list to show newly uploaded resume
        await fetchResumes()
        
        // Remove upload status after 3 seconds
        setTimeout(() => {
          setUploads((prev) => {
            const newUploads = { ...prev }
            delete newUploads[uploadId]
            return newUploads
          })
        }, 3000)
      }
    } catch (error: any) {
      console.error('Upload failed:', error)
      const errorMessage = error.message || 'Upload failed. Please try again.'
      setUploads((prev) => ({ 
        ...prev, 
        [uploadId]: { status: 'error', progress: 0, error: errorMessage }
      }))
    } finally {
      setUploadingFileId(null)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      handleFileUpload(files[0])
    }
    // Reset input so selecting the same file again will trigger change event
    e.target.value = ''
  }

  const handleDeleteResume = async (resumeId: string, resumeName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${resumeName}"?`)) {
      return
    }

    try {
      await resumeService.deleteResume(resumeId)
      
      // Refresh resume list
      await fetchResumes()
      
      // Show success message (you can add a toast notification here)
      console.log('Resume deleted successfully')
    } catch (error: any) {
      console.error('Delete failed:', error)
      alert(`Failed to delete resume: ${error.message}`)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateString: string | Date) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getUploadStatusColor = (status: UploadStatus) => {
    switch (status) {
      case 'uploading': return 'primary'
      case 'processing': return 'warning'
      case 'completed': return 'success'
      case 'error': return 'error'
      default: return 'neutral'
    }
  }

  return (
    <AppShell
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
              id="file-input"
              accept=".pdf,.doc,.docx,.txt,.rtf,.odt,.html,.md"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              disabled={loading}
            />
            <Button 
              variant="primary" 
              size="lg" 
              icon={<Plus size={20} />}
              onClick={() => document.getElementById('file-input')?.click()}
            >
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
            {Object.entries(uploads).map(([id, uploadState]) => (
              <div key={id} className="resumes-upload-progress">
                <div className="resumes-progress-header">
                  <span>
                    {uploadState.status === 'uploading' && `Uploading... ${uploadState.progress}%`}
                    {uploadState.status === 'processing' && 'Processing resume...'}
                    {uploadState.status === 'completed' && 'Upload completed'}
                    {uploadState.status === 'error' && 'Upload failed'}
                  </span>
                  {uploadState.status === 'uploading' && <Loader2 className="resumes-spinner" size={16} />}
                  {uploadState.status === 'processing' && <Badge variant="warning">Processing</Badge>}
                  {uploadState.status === 'completed' && <Badge variant="success">Completed</Badge>}
                  {uploadState.status === 'error' && <Badge variant="error">Failed</Badge>}
                </div>
                {uploadState.status !== 'error' ? (
                  <Progress 
                    value={uploadState.progress} 
                    color={uploadState.status === 'completed' ? 'success' : 'primary'}
                  />
                ) : (
                  <div style={{ 
                    padding: '12px', 
                    backgroundColor: 'var(--color-error-50, #fee2e2)', 
                    borderRadius: '6px',
                    color: 'var(--color-error-700, #b91c1c)',
                    fontSize: '14px'
                  }}>
                    {uploadState.error}
                  </div>
                )}
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
                className={resume.is_primary ? 'resumes-card-primary' : ''}
              >
                <CardBody>
                  <div className="resumes-card-header">
                    <div className="resumes-file-info">
                      <span className="resumes-file-icon">{fileTypeIcons[resume.file_type] || '📄'}</span>
                      <div>
                        <h3>{resume.filename}</h3>
                        <p>{formatFileSize(resume.file_size)} • {formatDate(resume.uploaded_at)}</p>
                      </div>
                    </div>
                    {resume.is_primary && <Badge variant="primary">Primary</Badge>}
                  </div>

                  {/* Status Badges */}
                  <div className="resumes-status-badges">
                    <Badge variant={resume.extraction_status === 'completed' ? 'success' : resume.extraction_status === 'failed' ? 'error' : 'warning'}>
                      {resume.extraction_status === 'completed' ? <Check size={12} /> : <Clock size={12} />}
                      {resume.extraction_status === 'completed' && '✓ Extracted'}
                      {resume.extraction_status === 'pending' && 'Processing...'}
                      {resume.extraction_status === 'failed' && 'Extraction Failed'}
                      {!resume.extraction_status && 'Unknown'}
                    </Badge>
                  </div>

                  {/* Actions */}
                  <div className="resumes-card-actions">
                    <Link to={`/resumes/${resume.id}/analysis`} className="resumes-action-link">
                      <Button variant="primary" size="sm" icon={<Eye size={16} />}>
                        View Analysis
                      </Button>
                    </Link>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      icon={<Trash2 size={16} />}
                      onClick={() => handleDeleteResume(resume.id, resume.filename)}
                    >
                      Delete
                    </Button>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}
      </AppShellContent>
    </AppShell>
  )
}

Resumes.displayName = 'Resumes'