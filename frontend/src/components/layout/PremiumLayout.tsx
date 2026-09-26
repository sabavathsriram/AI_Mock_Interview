import React, { useState } from 'react'
import { Menu, X, Bell, Settings, User, Moon, Sun } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'
import './PremiumLayout.css'

interface PremiumLayoutProps {
  children: React.ReactNode
  currentPage?: string
}

const navigationItems = [
  { id: 'overview', label: 'Overview', icon: '📊', href: '/dashboard' },
  { id: 'resume', label: 'Resume Intelligence', icon: '📄', href: '/resumes' },
  { id: 'job', label: 'Job Alignment', icon: '🎯', href: '/job-descriptions' },
  { id: 'interview', label: 'Interview', icon: '💬', href: '/interview/setup' },
  { id: 'history', label: 'Interview History', icon: '📋', href: '/interview-history' },
  { id: 'skills', label: 'Skill Intelligence', icon: '⚡', href: '/skills' },
  { id: 'learning', label: 'Learning Path', icon: '🎓', href: '/learning' },
  { id: 'progress', label: 'Progress', icon: '📈', href: '/progress' },
]

export const PremiumLayout: React.FC<PremiumLayoutProps> = ({ children, currentPage }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [sidebarMobile, setSidebarMobile] = useState(false)
  const { isDarkMode, toggleDarkMode } = useTheme()

  return (
    <div className="premium-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'collapsed'} ${sidebarMobile ? 'mobile-open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-mark">AI</div>
            {sidebarOpen && <span className="logo-text">Interview Intelligence</span>}
          </div>
          {sidebarMobile && (
            <button className="close-btn" onClick={() => setSidebarMobile(false)}>
              <X size={24} />
            </button>
          )}
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <a
              key={item.id}
              href={item.href}
              className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
              onClick={() => setSidebarMobile(false)}
            >
              <span className="nav-icon">{item.icon}</span>
              {sidebarOpen && <span className="nav-label">{item.label}</span>}
            </a>
          ))}
        </nav>

        <div className="sidebar-footer">
          <a href="/settings" className="nav-item">
            <span className="nav-icon">⚙️</span>
            {sidebarOpen && <span className="nav-label">Settings</span>}
          </a>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarMobile && (
        <div className="sidebar-overlay" onClick={() => setSidebarMobile(false)} />
      )}

      {/* Main content */}
      <div className="main-wrapper">
        {/* Top bar */}
        <header className="top-bar">
          <div className="top-bar-left">
            <button
              className="sidebar-toggle"
              onClick={() =>
                window.innerWidth < 1024
                  ? setSidebarMobile(!sidebarMobile)
                  : setSidebarOpen(!sidebarOpen)
              }
            >
              {sidebarOpen || sidebarMobile ? <X size={24} /> : <Menu size={24} />}
            </button>
            <input
              type="text"
              placeholder="Search interviews, skills, resources..."
              className="search-input"
            />
          </div>

          <div className="top-bar-right">
            <button className="icon-btn notification-btn">
              <Bell size={20} />
              <span className="badge">3</span>
            </button>
            <button className="icon-btn" onClick={toggleDarkMode}>
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <div className="user-menu">
              <button className="user-btn">
                <div className="user-avatar">AM</div>
              </button>
              <div className="dropdown-menu">
                <a href="/profile">Profile</a>
                <a href="/settings">Settings</a>
                <hr />
                <a href="#logout" style={{ color: 'var(--color-error-600)' }}>
                  Logout
                </a>
              </div>
            </div>
          </div>
        </header>

        {/* Content area */}
        <main className="content-area">{children}</main>
      </div>
    </div>
  )
}

PremiumLayout.displayName = 'PremiumLayout'