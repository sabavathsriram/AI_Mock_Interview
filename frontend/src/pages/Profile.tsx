import React, { useState } from 'react'
import {
  Mail,
  Briefcase,
  Target,
  Edit,
  Camera,
  Loader,
  RefreshCw,
  AlertCircle,
} from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Button } from '@/components/common'
import { Badge } from '@/components/Badge'
import { userService } from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'
import { useApi } from '@/hooks/useApi'
import { formatErrorMessage } from '@/utils/errors'
import './Profile.css'

export const Profile: React.FC = () => {
  const { user } = useAuth()

  // Use the useApi hook for profile data
  const {
    data: profileData,
    isLoading: isProfileLoading,
    error: profileError,
    fetchData: fetchProfile,
  } = useApi(
    async () => {
      try {
        const response = await userService.getUserProfile()
        return response.data
      } catch (error) {
        // Profile endpoint not yet implemented, this is expected
        console.debug('Profile endpoint not available')
        return null
      }
    },
    { immediate: true }
  )

  // Use the useApi hook for stats data
  const {
    data: statsData,
    isLoading: isStatsLoading,
    error: statsError,
    fetchData: fetchStats,
  } = useApi(
    async () => {
      try {
        const response = await userService.getUserStats()
        return response.data
      } catch (error) {
        // Stats endpoint not yet implemented, this is expected
        console.debug('Stats endpoint not available')
        return null
      }
    },
    { immediate: true }
  )

  const isLoading = isProfileLoading || isStatsLoading
  const error = profileError || statsError

  // Refresh both data sources
  const refreshData = () => {
    fetchProfile()
    fetchStats()
  }

  if (isLoading) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Profile' },
        ]}
      >
        <AppShellContent>
          <div className="profile-loading">
            <Loader className="profile-loading-icon" size={32} />
            <p>Loading profile data...</p>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  if (error) {
    return (
      <AppShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Profile' },
        ]}
      >
        <AppShellContent>
          <div className="profile-error">
            <AlertCircle size={24} />
            <div>
              <h3>Error loading profile</h3>
              <p>{formatErrorMessage(error)}</p>
            </div>
            <Button variant="secondary" size="sm" icon={<RefreshCw size={16} />} iconPosition="left" onClick={refreshData}>
              Try Again
            </Button>
          </div>
        </AppShellContent>
      </AppShell>
    )
  }

  // Use real data or fallback to user context data
  const displayProfile = profileData || {
    full_name: user?.full_name || '',
    email: user?.email || '',
    job_title: '',
    experience_years: 0,
    preferred_interview_types: [],
    skills: [],
  }

  const displayStats = statsData || {
    total_interviews: 0,
    average_score: 0,
    best_score: 0,
  }

  return (
    <AppShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Profile' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="profile-page">
          {/* Header */}
          <div className="profile-header">
            <div className="profile-header-content">
              <h1>My Profile</h1>
              <p>View and manage your profile information</p>
            </div>
            <div className="profile-header-actions">
              <Button variant="ghost" size="sm" icon={<RefreshCw size={16} />} iconPosition="left" onClick={refreshData} disabled={isLoading}>
                Refresh
              </Button>
              <Button variant="primary" size="sm" icon={<Edit size={16} />} iconPosition="left">
                Edit Profile
              </Button>
            </div>
          </div>

          {/* Profile Header Card */}
          <Card variant="elevated" padding="lg" className="profile-header-card">
            <CardBody>
              <div className="profile-header-layout">
                <div className="profile-avatar-section">
                  <div className="profile-avatar">
                    {displayProfile.full_name.split(' ').map((n: string) => n[0]).join('')}
                  </div>
                  <button className="profile-avatar-edit" title="Change avatar">
                    <Camera size={16} />
                  </button>
                </div>
                <div className="profile-intro">
                  <h2>{displayProfile.full_name}</h2>
                  <p className="profile-email">{displayProfile.email}</p>
                  <div className="profile-badges">
                    <Badge variant="primary" size="sm">{displayProfile.job_title || 'Software Developer'}</Badge>
                    <Badge variant="secondary" size="sm">{displayProfile.experience_years || 0} years experience</Badge>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Stats Grid */}
          <div className="profile-stats-grid">
            {[
              { label: 'Interviews', value: displayStats.total_interviews || 0 },
              { label: 'Avg Score', value: `${displayStats.average_score || 0}%` },
              { label: 'Best Score', value: `${displayStats.best_score || 0}%` },
              { label: 'Skills', value: displayProfile.skills?.length || 0 },
            ].map((stat, index) => (
              <Card key={index} variant="default" padding="md" className="profile-stat-card">
                <CardBody>
                  <p className="profile-stat-value">{stat.value}</p>
                  <p className="profile-stat-label">{stat.label}</p>
                </CardBody>
              </Card>
            ))}
          </div>

          {/* Details Grid */}
          <div className="profile-details-grid">
            <Card variant="default" padding="lg" className="profile-section">
              <CardHeader>
                <div className="profile-section-header">
                  <Briefcase size={20} />
                  <h3>Professional Info</h3>
                </div>
              </CardHeader>
              <CardBody>
                <div className="profile-detail-list">
                  <div className="profile-detail-item">
                    <label>Job Title</label>
                    <p>{displayProfile.job_title || 'Not specified'}</p>
                  </div>
                  <div className="profile-detail-item">
                    <label>Experience</label>
                    <p>{displayProfile.experience_years || 0} years</p>
                  </div>
                  <div className="profile-detail-item">
                    <label>Preferred Interview Types</label>
                    <p>{displayProfile.preferred_interview_types?.join(', ') || 'Technical'}</p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card variant="default" padding="lg" className="profile-section">
              <CardHeader>
                <div className="profile-section-header">
                  <Target size={20} />
                  <h3>Skills</h3>
                </div>
              </CardHeader>
              <CardBody>
                {displayProfile.skills && displayProfile.skills.length > 0 ? (
                  <div className="profile-skills-tags">
                    {displayProfile.skills.map((skill: string) => (
                      <Badge key={skill} variant="primary" size="sm">{skill}</Badge>
                    ))}
                  </div>
                ) : (
                  <p className="profile-empty-state">No skills added yet</p>
                )}
              </CardBody>
            </Card>
          </div>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Profile.displayName = 'Profile'