import React from 'react'
import './Card.css'

export type CardVariant = 'default' | 'elevated' | 'ghost'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant
  padding?: 'sm' | 'md' | 'lg'
}

/**
 * Card Component
 * A flexible container component for grouping related content
 */
export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', padding = 'md', className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={['card', `card-${variant}`, `card-padding-${padding}`, className]
          .filter(Boolean)
          .join(' ')}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

/* ============================================================================
   CARD SECTIONS - Semantic sub-components
   ============================================================================ */

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, children, ...props }, ref) => (
    <div ref={ref} className={['card-header', className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  )
)

CardHeader.displayName = 'CardHeader'

export interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardBody = React.forwardRef<HTMLDivElement, CardBodyProps>(
  ({ className, children, ...props }, ref) => (
    <div ref={ref} className={['card-body', className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  )
)

CardBody.displayName = 'CardBody'

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, children, ...props }, ref) => (
    <div ref={ref} className={['card-footer', className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  )
)

CardFooter.displayName = 'CardFooter'
