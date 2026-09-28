import React, { useState } from 'react'
import { Menu, Moon, Sun, Bell, Search } from 'lucide-react'
import { UserMenu } from './UserMenu'
import { useAuth } from '@/contexts/AuthContext'
import { useTheme } from '@/contexts/ThemeContext'
import './TopNav.css'

interface TopNavProps {
  onMenuClick?: () => void
  showSearch?: boolean
}

/**
 * TopNav Component
 * Fixed top navigation bar with search, notifications, theme toggle, and user menu
 */
export const TopNav: React.FC<TopNavProps> = ({
  onMenuClick,
  showSearch = true,
}) => {
  const { isDarkMode, toggleDarkMode } = useTheme()
  const { user } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')

  const userName = user?.full_name || 'User'
  const userEmail = user?.email || ''

  return (
    <header className="top-nav">
      {/* Left section */}
      <div className="top-nav-left">
        {/* Menu button - mobile only */}
        <button
          onClick={onMenuClick}
          className="top-nav-menu-btn"
          aria-label="Toggle sidebar"
          title="Toggle sidebar"
        >
          <Menu size={20} />
        </button>

        {/* Search bar */}
        {showSearch && (
          <div className="top-nav-search">
            <div className="top-nav-search-icon">
              <Search size={18} />
            </div>
            <input
              type="text"
              placeholder="Search interviews, skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="top-nav-search-input"
              aria-label="Search"
            />
          </div>
        )}
      </div>

      {/* Right section */}
      <div className="top-nav-right">
        {/* Notifications */}
        <button
          className="top-nav-icon-btn"
          aria-label="Notifications"
          title="Notifications"
        >
          <Bell size={20} />
          <span className="top-nav-notification-badge" />
        </button>

        {/* Dark mode toggle */}
        <button
          onClick={toggleDarkMode}
          className="top-nav-icon-btn"
          aria-label="Toggle dark mode"
          title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        {/* Divider */}
        <div className="top-nav-divider" aria-hidden="true" />

        {/* User menu */}
        <UserMenu
          userName={userName}
          userEmail={userEmail}
        />
      </div>
    </header>
  )
}

TopNav.displayName = 'TopNav'
