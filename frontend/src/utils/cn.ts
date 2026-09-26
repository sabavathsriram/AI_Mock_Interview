import clsx from 'clsx'

/**
 * Utility function to combine Tailwind CSS classes
 * Useful for conditional and dynamic class application
 */
export function cn(...classes: (string | undefined | null | boolean | Record<string, boolean>)[]): string {
  return clsx(...classes)
}

export default cn
