import React, { useState } from 'react'
import { Sidebar } from './Sidebar'
import { TopNav } from './TopNav'
import { Breadcrumbs } from './Breadcrumbs'
import '../layout/AppShell.css'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface AppShellProps {
  children: React.ReactNode
  breadcrumbs?: BreadcrumbItem[]
  showBreadcrumbs?: boolean
  showTopNav?: boolean
  showSidebar?: boolean
  isDarkMode?: boolean
  onToggleDarkMode?: () => void
  userName?: string
  userEmail?: string
  onLogout?: () => void
  className?: string
  contentClassName?: string
}

/**
 * AppShell Component
 * Main application layout with proper flexbox architecture
 * Prevents sidebar/content overlap at all breakpoints
 * 
 * Layout structure:
 * - Top navigation: fixed height, sticky at top
 * - Sidebar: fixed width on desktop, overlay on mobile
 * - Main content: fills remaining space, scrollable
 */
export const AppShell: React.FC<AppShellProps> = ({
  children,
  breadcrumbs,
  showBreadcrumbs = true,
  showTopNav = true,
  showSidebar = true,
  isDarkMode = false,
  onToggleDarkMode,
  userName = 'Alex Morgan',
  userEmail = 'alex@example.com',
  onLogout,
  className,
  contentClassName,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div
      className={['app-shell', className].filter(Boolean).join(' ')}
      data-theme={isDarkMode ? 'dark' : 'light'}
    >
      {/* Top Navigation - Sticky */}
      {showTopNav && (
        <TopNav
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          onToggleDarkMode={onToggleDarkMode}
          isDarkMode={isDarkMode}
          userName={userName}
          userEmail={userEmail}
          onLogout={onLogout}
        />
      )}

      {/* Main container with sidebar and content */}
      <div className="app-shell-body">
        {/* Sidebar */}
        {showSidebar && (
          <>
            {/* Sidebar backdrop for mobile */}
            {sidebarOpen && (
              <div
                className="app-shell-backdrop"
                onClick={() => setSidebarOpen(false)}
                aria-hidden="true"
              />
            )}
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          </>
        )}

        {/* Main Content Area */}
        <main className="app-shell-main">
          <div className={['app-shell-content', contentClassName].filter(Boolean).join(' ')}>
            {/* Breadcrumbs */}
            {showBreadcrumbs && breadcrumbs && breadcrumbs.length > 0 && (
              <div className="app-shell-breadcrumbs">
                <Breadcrumbs items={breadcrumbs} />
              </div>
            )}

            {/* Page content */}
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

AppShell.displayName = 'AppShell'

interface AppShellContentProps {
  children: React.ReactNode
  className?: string
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
}

const maxWidthClasses = {
  sm: 'max-width-sm',
  md: 'max-width-md',
  lg: 'max-width-lg',
  xl: 'max-width-xl',
  '2xl': 'max-width-2xl',
  full: 'max-width-full',
}

/**
 * AppShellContent Component
 * Content wrapper with optional max-width constraint and padding
 */
export const AppShellContent: React.FC<AppShellContentProps> = ({
  children,
  className,
  maxWidth = 'full',
}) => {
  const contentClass = [
    'app-shell-section',
    maxWidthClasses[maxWidth],
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return <div className={contentClass}>{children}</div>
}

AppShellContent.displayName = 'AppShellContent'

interface AppShellHeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
  className?: string
}

/**
 * AppShellHeader Component
 * Page header with title, optional subtitle, and action slot
 */
export const AppShellHeader: React.FC<AppShellHeaderProps> = ({
  title,
  subtitle,
  action,
  className,
}) => {
  return (
    <div className={['app-shell-header', className].filter(Boolean).join(' ')}>
      <div className="app-shell-header-content">
        <h1 className="app-shell-title">{title}</h1>
        {subtitle && <p className="app-shell-subtitle">{subtitle}</p>}
      </div>
      {action && <div className="app-shell-header-action">{action}</div>}
    </div>
  )
}

AppShellHeader.displayName = 'AppShellHeader'
