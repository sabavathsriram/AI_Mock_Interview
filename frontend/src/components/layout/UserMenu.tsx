import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut, Settings, User, ChevronDown } from 'lucide-react'
import { cn } from '@/utils/cn'

interface UserMenuProps {
  userName: string
  userEmail?: string
  onLogout?: () => void
}

export const UserMenu: React.FC<UserMenuProps> = ({ userName, userEmail, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleLogout = () => {
    onLogout?.()
    navigate('/login')
    setIsOpen(false)
  }

  const handleProfileClick = () => {
    navigate('/profile')
    setIsOpen(false)
  }

  const handleSettingsClick = () => {
    navigate('/settings')
    setIsOpen(false)
  }

  // Extract initials
  const initials = userName
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase()

  return (
    <div ref={containerRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg transition-colors',
          'text-dark-600 dark:text-dark-400 hover:bg-dark-100 dark:hover:bg-dark-700',
          isOpen && 'bg-dark-100 dark:bg-dark-700',
        )}
      >
        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-sm font-bold">
          {initials}
        </div>

        {/* Name and email */}
        <div className="hidden sm:flex flex-col items-start">
          <span className="text-sm font-medium text-dark-900 dark:text-white">{userName}</span>
          {userEmail && (
            <span className="text-xs text-dark-500 dark:text-dark-400">{userEmail}</span>
          )}
        </div>

        {/* Chevron */}
        <ChevronDown
          size={18}
          className={cn(
            'text-dark-400 dark:text-dark-500 transition-transform duration-200',
            isOpen && 'rotate-180',
          )}
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-dark-800 rounded-lg shadow-lg border border-dark-200 dark:border-dark-700 z-50 animate-slide-up">
          {/* User info */}
          <div className="px-4 py-3 border-b border-dark-200 dark:border-dark-700">
            <p className="text-sm font-semibold text-dark-900 dark:text-white">{userName}</p>
            {userEmail && (
              <p className="text-xs text-dark-500 dark:text-dark-400 truncate">{userEmail}</p>
            )}
          </div>

          {/* Menu items */}
          <div className="py-1">
            <button
              onClick={handleProfileClick}
              className="w-full px-4 py-2 text-sm text-left flex items-center gap-2 text-dark-700 dark:text-dark-300 hover:bg-dark-100 dark:hover:bg-dark-700 transition-colors"
            >
              <User size={16} />
              <span>Profile</span>
            </button>

            <button
              onClick={handleSettingsClick}
              className="w-full px-4 py-2 text-sm text-left flex items-center gap-2 text-dark-700 dark:text-dark-300 hover:bg-dark-100 dark:hover:bg-dark-700 transition-colors"
            >
              <Settings size={16} />
              <span>Settings</span>
            </button>
          </div>

          {/* Logout */}
          <div className="border-t border-dark-200 dark:border-dark-700 py-1">
            <button
              onClick={handleLogout}
              className="w-full px-4 py-2 text-sm text-left flex items-center gap-2 text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20 transition-colors"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

UserMenu.displayName = 'UserMenu'
