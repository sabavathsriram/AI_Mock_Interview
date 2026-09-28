import React, { useState } from 'react'
import { Briefcase } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Button } from '@/components/Button'
import './JobDescriptions.css'

export const JobDescriptions: React.FC = () => {
  return (
    <AppShell
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
        </div>

        {/* Empty State */}
        <div style={{ 
          padding: '80px 20px', 
          textAlign: 'center', 
          color: 'var(--color-text-secondary)' 
        }}>
          <Briefcase size={64} style={{ marginBottom: '20px', opacity: 0.5 }} />
          <h2 style={{ marginBottom: '10px', color: 'var(--color-text-primary)' }}>Job Description Feature Coming Soon</h2>
          <p style={{ marginBottom: '20px', maxWidth: '500px', margin: '0 auto 20px' }}>
            The ability to add and manage job descriptions for interview preparation is coming soon. 
            This feature will help you align your resume with target positions and identify skill gaps.
          </p>
          <p style={{ fontSize: '14px', opacity: 0.7 }}>Backend API not yet implemented</p>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

JobDescriptions.displayName = 'JobDescriptions'
