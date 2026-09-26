import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Menu,
  X,
  LayoutDashboard,
  FileText,
  Briefcase,
  Zap,
  Clock,
  TrendingUp,
  BookOpen,
  Settings,
} from 'lucide-react'
import './Sidebar.css'

interface SidebarItem {
  label: string
  href: string
  icon: React.ReactNode
  badge?: string | number
}

const navItems: SidebarItem[] = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: <LayoutDashboard size={20} />,
  },
  {
    label: 'Resumes',
    href: '/resumes',
    icon: <FileText size={20} />,
  },
  {
    label: 'Job Descriptions',
    href: '/job-descriptions',
    icon: <Briefcase size={20} />,
  },
  {
    label: 'Mock Interview',
    href: '/interview/setup',
    icon: <Zap size={20} />,
  },
  {
    label: 'Interview History',
    href: '/interview-history',
    icon: <Clock size={20} />,
  },
  {
    label: 'Skill Analysis',
    href: '/skills',
    icon: <TrendingUp size={20} />,
  },
  {
    label: 'Learning Roadmap',
    href: '/learning',
    icon: <BookOpen size={20} />,
  },
  {
    label: 'Settings',
    href: '/settings',
    icon: <Settings size={20} />,
  },
]

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

/**
 * Sidebar Component
 * Responsive navigation sidebar with collapse functionality
 * Desktop: always visible, can collapse to icon-only
 * Mobile: overlay drawer, hidden by default
 */
export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const location = useLocation()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const isActive = (href: string) =>
    location.pathname === href || location.pathname.startsWith(href + '/')

  const sidebarClasses = ['sidebar', isOpen && 'open', isCollapsed && 'collapsed']
    .filter(Boolean)
    .join(' ')

  return (
    <aside className={sidebarClasses} role="navigation" aria-label="Main navigation">
      {/* Header with Logo */}
      <div className="sidebar-header">
        {!isCollapsed && (
          <Link to="/dashboard" className="sidebar-logo">
            <div className="sidebar-logo-icon">AI</div>
            <span className="sidebar-logo-text">MockInterview</span>
          </Link>
        )}

        {/* Toggle buttons */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="sidebar-toggle toggle-collapse"
          aria-label="Toggle sidebar collapse"
          title="Toggle sidebar"
        >
          <Menu size={18} />
        </button>

        <button
          onClick={onClose}
          className="sidebar-toggle toggle-close"
          aria-label="Close sidebar"
          title="Close sidebar"
        >
          <X size={18} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <ul>
          {navItems.map((item) => (
            <li key={item.href}>
              <Link
                to={item.href}
                className={[
                  'sidebar-nav-item',
                  isActive(item.href) && 'active',
                ]
                  .filter(Boolean)
                  .join(' ')}
                title={isCollapsed ? item.label : undefined}
              >
                <span className="sidebar-nav-icon">{item.icon}</span>
                <span className="sidebar-nav-label">{item.label}</span>
                {item.badge && (
                  <span className="sidebar-nav-badge">{item.badge}</span>
                )}
                {isCollapsed && (
                  <div className="sidebar-tooltip">{item.label}</div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <p className="sidebar-footer-text">
          © 2024 AI Mock Interview System
        </p>
      </div>
    </aside>
  )
}

Sidebar.displayName = 'Sidebar'
