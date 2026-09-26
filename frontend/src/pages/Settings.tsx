import React, { useState } from 'react'
import {
  User,
  Palette,
  Bell,
  Shield,
  Database,
  Moon,
  Sun,
  Save,
  Download,
  Trash2,
} from 'lucide-react'
import { AppShell, AppShellContent } from '@/components/layout'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Button } from '@/components/common'
import { Input } from '@/components/common'
import { mockCurrentUser } from '@/data/mockData'
import './Settings.css'

const tabs = [
  { id: 'account', label: 'Account', icon: <User size={18} /> },
  { id: 'appearance', label: 'Appearance', icon: <Palette size={18} /> },
  { id: 'notifications', label: 'Notifications', icon: <Bell size={18} /> },
  { id: 'privacy', label: 'Privacy', icon: <Shield size={18} /> },
  { id: 'data', label: 'Data', icon: <Database size={18} /> },
]

export const Settings: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [activeTab, setActiveTab] = useState('account')
  const [settings, setSettings] = useState({
    name: mockCurrentUser.name,
    email: mockCurrentUser.email,
    targetRole: mockCurrentUser.targetRole,
    experienceLevel: mockCurrentUser.experienceLevel,
    preferredInterviewType: mockCurrentUser.preferredInterviewType,
    emailNotifications: true,
    pushNotifications: false,
    weeklyDigest: true,
    interviewReminders: true,
    publicProfile: false,
    showProgress: true,
  })

  const notificationSettings = [
    { key: 'emailNotifications', label: 'Email Notifications', desc: 'Receive updates via email' },
    { key: 'pushNotifications', label: 'Push Notifications', desc: 'Browser push notifications' },
    { key: 'weeklyDigest', label: 'Weekly Digest', desc: 'Weekly progress summary' },
    { key: 'interviewReminders', label: 'Interview Reminders', desc: 'Reminders before scheduled interviews' },
  ]

  const privacySettings = [
    { key: 'publicProfile', label: 'Public Profile', desc: 'Allow others to view your profile' },
    { key: 'showProgress', label: 'Show Progress', desc: 'Display your progress on public profile' },
  ]

  return (
    <AppShell
      isDarkMode={isDarkMode}
      onToggleDarkMode={() => setIsDarkMode(!isDarkMode)}
      userName="Alex Morgan"
      userEmail="alex@example.com"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Settings' },
      ]}
    >
      <AppShellContent maxWidth="full">
        <div className="settings-page">
          {/* Header */}
          <div className="settings-header">
            <div className="settings-header-content">
              <h1>Settings</h1>
              <p>Manage your account and preferences</p>
            </div>
          </div>

          {/* Layout */}
          <div className="settings-layout">
            {/* Sidebar */}
            <div className="settings-sidebar">
              <Card variant="default" padding="sm" className="settings-nav-card">
                <CardBody>
                  <div className="settings-nav">
                    {tabs.map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`settings-nav-item ${activeTab === tab.id ? 'active' : ''}`}
                      >
                        {tab.icon}
                        <span>{tab.label}</span>
                      </button>
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Content */}
            <div className="settings-content">
              {/* Account Settings */}
              {activeTab === 'account' && (
                <Card variant="default" padding="lg" className="settings-section-card">
                  <CardHeader>
                    <h2>Account Settings</h2>
                    <p className="settings-section-description">Manage your personal information</p>
                  </CardHeader>
                  <CardBody>
                    <div className="settings-form-group">
                      <label>Full Name</label>
                      <Input
                        value={settings.name}
                        onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                      />
                    </div>
                    <div className="settings-form-group">
                      <label>Email</label>
                      <Input
                        type="email"
                        value={settings.email}
                        onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                      />
                    </div>
                    <div className="settings-form-group">
                      <label>Target Role</label>
                      <Input
                        value={settings.targetRole}
                        onChange={(e) => setSettings({ ...settings, targetRole: e.target.value })}
                      />
                    </div>
                    <div className="settings-form-group">
                      <label>Experience Level</label>
                      <select className="settings-select" value={settings.experienceLevel} onChange={(e) => setSettings({ ...settings, experienceLevel: e.target.value })}>
                        <option value="Entry">Entry Level (0-2 years)</option>
                        <option value="Mid">Mid-Level (2-5 years)</option>
                        <option value="Senior">Senior (5-10 years)</option>
                        <option value="Lead">Lead/Principal (10+ years)</option>
                      </select>
                    </div>
                    <div className="settings-form-group">
                      <label>Preferred Interview Type</label>
                      <select className="settings-select" value={settings.preferredInterviewType} onChange={(e) => setSettings({ ...settings, preferredInterviewType: e.target.value })}>
                        <option value="Technical">Technical</option>
                        <option value="Behavioral">Behavioral</option>
                        <option value="Mixed">Mixed</option>
                      </select>
                    </div>
                    <Button variant="primary" size="md" icon={<Save size={18} />} iconPosition="left">
                      Save Changes
                    </Button>
                  </CardBody>
                </Card>
              )}

              {/* Appearance Settings */}
              {activeTab === 'appearance' && (
                <Card variant="default" padding="lg" className="settings-section-card">
                  <CardHeader>
                    <h2>Appearance</h2>
                    <p className="settings-section-description">Customize how the app looks</p>
                  </CardHeader>
                  <CardBody>
                    <div className="settings-toggle-item">
                      <div className="settings-toggle-content">
                        <p className="settings-toggle-label">Dark Mode</p>
                        <p className="settings-toggle-description">Use dark theme for the interface</p>
                      </div>
                      <button
                        onClick={() => setIsDarkMode(!isDarkMode)}
                        className={`settings-toggle ${isDarkMode ? 'active' : ''}`}
                      >
                        {isDarkMode ? <Moon size={18} /> : <Sun size={18} />}
                      </button>
                    </div>
                  </CardBody>
                </Card>
              )}

              {/* Notifications Settings */}
              {activeTab === 'notifications' && (
                <Card variant="default" padding="lg" className="settings-section-card">
                  <CardHeader>
                    <h2>Notification Preferences</h2>
                    <p className="settings-section-description">Control how you receive notifications</p>
                  </CardHeader>
                  <CardBody>
                    <div className="settings-toggles-list">
                      {notificationSettings.map((item) => (
                        <div key={item.key} className="settings-toggle-item">
                          <div className="settings-toggle-content">
                            <p className="settings-toggle-label">{item.label}</p>
                            <p className="settings-toggle-description">{item.desc}</p>
                          </div>
                          <button
                            onClick={() => setSettings({ ...settings, [item.key]: !settings[item.key as keyof typeof settings] })}
                            className={`settings-checkbox ${settings[item.key as keyof typeof settings] ? 'checked' : ''}`}
                          >
                            {settings[item.key as keyof typeof settings] && '✓'}
                          </button>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>
              )}

              {/* Privacy Settings */}
              {activeTab === 'privacy' && (
                <Card variant="default" padding="lg" className="settings-section-card">
                  <CardHeader>
                    <h2>Privacy Settings</h2>
                    <p className="settings-section-description">Control your data and privacy</p>
                  </CardHeader>
                  <CardBody>
                    <div className="settings-toggles-list">
                      {privacySettings.map((item) => (
                        <div key={item.key} className="settings-toggle-item">
                          <div className="settings-toggle-content">
                            <p className="settings-toggle-label">{item.label}</p>
                            <p className="settings-toggle-description">{item.desc}</p>
                          </div>
                          <button
                            onClick={() => setSettings({ ...settings, [item.key]: !settings[item.key as keyof typeof settings] })}
                            className={`settings-checkbox ${settings[item.key as keyof typeof settings] ? 'checked' : ''}`}
                          >
                            {settings[item.key as keyof typeof settings] && '✓'}
                          </button>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>
              )}

              {/* Data Management */}
              {activeTab === 'data' && (
                <Card variant="default" padding="lg" className="settings-section-card">
                  <CardHeader>
                    <h2>Data Management</h2>
                    <p className="settings-section-description">Export or delete your data</p>
                  </CardHeader>
                  <CardBody>
                    <div className="settings-data-actions">
                      <div className="settings-data-action">
                        <div className="settings-data-action-content">
                          <p className="settings-data-action-label">Export Data</p>
                          <p className="settings-data-action-description">
                            Download all your data including interview history, progress, and settings
                          </p>
                        </div>
                        <Button variant="secondary" size="sm" icon={<Download size={16} />} iconPosition="left">
                          Export
                        </Button>
                      </div>
                      <div className="settings-data-action danger">
                        <div className="settings-data-action-content">
                          <p className="settings-data-action-label">Delete Account</p>
                          <p className="settings-data-action-description">
                            Permanently delete your account and all associated data
                          </p>
                        </div>
                        <Button variant="error" size="sm" icon={<Trash2 size={16} />} iconPosition="left">
                          Delete
                        </Button>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          </div>

          {/* Demo Notice */}
          <Card variant="default" padding="md" className="settings-demo-notice">
            <CardBody>
              <p>📊 <strong>Demo Mode:</strong> Settings are not persisted. They will reset on page refresh.</p>
            </CardBody>
          </Card>
        </div>
      </AppShellContent>
    </AppShell>
  )
}

Settings.displayName = 'Settings'