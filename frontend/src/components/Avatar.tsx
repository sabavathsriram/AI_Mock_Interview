import React from 'react'
import './Avatar.css'

export type AvatarSize = 'sm' | 'md' | 'lg' | 'xl'

export interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  size?: AvatarSize
  name?: string
  src?: string
  initials?: string
  backgroundColor?: string
}

/**
 * Avatar Component
 * Displays a user avatar with optional initials fallback
 */
export const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  (
    {
      size = 'md',
      name,
      src,
      initials,
      backgroundColor,
      className,
      alt,
      ...props
    },
    ref
  ) => {
    // Generate initials from name if not provided
    const getInitials = (fullName: string | undefined) => {
      if (!fullName) return '?'
      return fullName
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    }

    const displayInitials = initials || getInitials(name)

    return (
      <div
        ref={ref}
        className={['avatar', `avatar-${size}`, className].filter(Boolean).join(' ')}
        title={name}
      >
        {src ? (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className="avatar-image"
            {...props}
          />
        ) : (
          <div
            className="avatar-initials"
            style={
              backgroundColor ? { backgroundColor } : undefined
            }
          >
            {displayInitials}
          </div>
        )}
      </div>
    )
  }
)

Avatar.displayName = 'Avatar'

/* ============================================================================
   AVATAR GROUP - Display multiple avatars
   ============================================================================ */

export interface AvatarGroupProps {
  avatars: Array<{
    name: string
    src?: string
    initials?: string
  }>
  max?: number
  size?: AvatarSize
}

export const AvatarGroup: React.FC<AvatarGroupProps> = ({
  avatars,
  max = 3,
  size = 'md',
}) => {
  const displayed = avatars.slice(0, max)
  const remaining = Math.max(0, avatars.length - max)

  return (
    <div className={['avatar-group', `avatar-group-${size}`].filter(Boolean).join(' ')}>
      {displayed.map((avatar, idx) => (
        <Avatar
          key={idx}
          {...avatar}
          size={size}
          className="avatar-group-item"
        />
      ))}
      {remaining > 0 && (
        <div className={['avatar', `avatar-${size}`, 'avatar-more'].join(' ')}>
          <span className="avatar-more-text">+{remaining}</span>
        </div>
      )}
    </div>
  )
}

AvatarGroup.displayName = 'AvatarGroup'
