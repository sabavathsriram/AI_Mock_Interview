/**
 * Theme utility functions for color management and styling variants
 */

import { DESIGN_SYSTEM } from '@/styles/design-system'

// Shorthand for colors
const Colors = DESIGN_SYSTEM.colors

export const colorVariants = {
  // Button variants
  button: {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white',
    secondary: 'bg-dark-100 hover:bg-dark-200 text-dark-900 dark:bg-dark-800 dark:hover:bg-dark-700 dark:text-white',
    success: 'bg-success-600 hover:bg-success-700 text-white',
    warning: 'bg-warning-600 hover:bg-warning-700 text-white',
    error: 'bg-error-600 hover:bg-error-700 text-white',
    ghost: 'hover:bg-dark-100 text-dark-900 dark:hover:bg-dark-800 dark:text-white',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-950',
  },

  // Badge variants
  badge: {
    primary: 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-100',
    secondary: 'bg-secondary-100 text-secondary-800 dark:bg-secondary-900 dark:text-secondary-100',
    success: 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-100',
    warning: 'bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-100',
    error: 'bg-error-100 text-error-800 dark:bg-error-900 dark:text-error-100',
  },

  // Card variants
  card: {
    default: 'bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700',
    elevated: 'bg-white dark:bg-dark-800 shadow-lg',
    ghost: 'border border-dark-200 dark:border-dark-700',
  },

  // Input variants
  input: {
    default: 'border border-dark-300 dark:border-dark-600 bg-white dark:bg-dark-800 focus:border-primary-500 dark:focus:border-primary-400',
    filled: 'border border-dark-300 dark:border-dark-600 bg-dark-50 dark:bg-dark-700',
  },

  // Text variants
  text: {
    primary: 'text-dark-900 dark:text-white',
    secondary: 'text-dark-600 dark:text-dark-400',
    tertiary: 'text-dark-500 dark:text-dark-500',
    muted: 'text-dark-400 dark:text-dark-600',
  },
} as const;

export const severityColors = {
  low: Colors.success,
  medium: Colors.warning,
  high: Colors.error,
} as const;

export const skillLevelColors = {
  beginner: Colors.error,
  intermediate: Colors.warning,
  advanced: Colors.success,
} as const;

export const performanceGradient = (score: number) => {
  if (score >= 80) return Colors.success[500];
  if (score >= 60) return Colors.warning[500];
  return Colors.error[500];
};

export const getDifficultyColor = (difficulty: string) => {
  switch (difficulty?.toLowerCase()) {
    case 'easy':
      return Colors.success[500];
    case 'medium':
      return Colors.warning[500];
    case 'hard':
      return Colors.error[500];
    default:
      return Colors.primary[500];
  }
};

export default {
  colorVariants,
  severityColors,
  skillLevelColors,
  performanceGradient,
  getDifficultyColor,
}
