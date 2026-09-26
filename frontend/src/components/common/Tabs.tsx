import React, { useState } from 'react'
import './Tabs.css'

interface TabItem {
  label: string
  value: string
  icon?: React.ReactNode
  badge?: string | number
  disabled?: boolean
}

interface TabsProps {
  items: TabItem[]
  defaultValue?: string
  onChange?: (value: string) => void
  className?: string
  variant?: 'line' | 'pill'
}

/**
 * Tabs Component
 * Provides tabbed navigation with line and pill variants
 */
export const Tabs: React.FC<TabsProps> = ({
  items,
  defaultValue,
  onChange,
  className,
  variant = 'line',
}) => {
  const [activeTab, setActiveTab] = useState(defaultValue || items[0]?.value)

  const handleTabChange = (value: string) => {
    setActiveTab(value)
    onChange?.(value)
  }

  const tabsClass = ['tabs', variant === 'pill' && 'tabs-pill', className]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={tabsClass} role="tablist">
      {items.map((item) => (
        <button
          key={item.value}
          role="tab"
          aria-selected={activeTab === item.value}
          disabled={item.disabled}
          onClick={() => !item.disabled && handleTabChange(item.value)}
          className={['tab', activeTab === item.value && 'tab-active']
            .filter(Boolean)
            .join(' ')}
        >
          {item.icon && <span className="tab-icon">{item.icon}</span>}
          <span>{item.label}</span>
          {item.badge && <span className="tab-badge">{item.badge}</span>}
        </button>
      ))}
    </div>
  )
}

Tabs.displayName = 'Tabs'

interface TabsContentProps {
  value: string
  children: React.ReactNode
  isActive: boolean
}

/**
 * TabsContent Component
 * Renders content for a specific tab
 */
export const TabsContent: React.FC<TabsContentProps> = ({ children, isActive }) => {
  if (!isActive) return null
  return (
    <div className="tab-content-enter" role="tabpanel">
      {children}
    </div>
  )
}

TabsContent.displayName = 'TabsContent'
