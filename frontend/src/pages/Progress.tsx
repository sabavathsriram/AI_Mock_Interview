import React from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody } from '@/components/Card'
import { Button } from '@/components/common'
import './Progress.css'

export const Progress: React.FC = () => {
  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Progress' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="progress-page">
          {/* Header */}
          <div className="progress-page-header">
            <div className="progress-page-header-content">
              <h1>Your Progress</h1>
              <p>Track your improvement over time</p>
            </div>
          </div>

          {/* Empty State */}
          <Card variant="default" padding="lg" className="progress-empty">
            <CardBody>
              <div className="progress-empty-content">
                <AlertCircle size={48} />
                <h3>Feature Coming Soon</h3>
                <p>Progress tracking is currently under development.</p>
                <p className="progress-empty-subtext">
                  Once you complete mock interviews, your progress data will appear here.
                </p>
                <Link to="/dashboard">
                  <Button variant="primary" size="sm">
                    Return to Dashboard
                  </Button>
                </Link>
              </div>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Progress.displayName = 'Progress'