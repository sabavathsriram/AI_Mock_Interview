import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/utils/cn'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  className?: string
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className }) => {
  return (
    <nav
      className={cn('flex items-center gap-2 text-sm', className)}
      aria-label="Breadcrumb"
    >
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <ChevronRight className="w-4 h-4 text-dark-400 dark:text-dark-600" />
          )}

          {item.href ? (
            <Link
              to={item.href}
              className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-dark-600 dark:text-dark-400">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  )
}

Breadcrumbs.displayName = 'Breadcrumbs'
