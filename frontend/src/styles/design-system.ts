/**
 * Premium AI Interview Intelligence Design System
 * 
 * Professional design tokens for a SaaS product interface
 */

export const DESIGN_SYSTEM = {
  // Brand Colors - AI-focused palette
  colors: {
    // Primary - Deep Blue (AI/Intelligence)
    primary: {
      50: '#f0f7ff',
      100: '#e0effe',
      200: '#c7e9ff',
      300: '#a3d8ff',
      400: '#74bbff',
      500: '#4b9aff', // Primary brand color
      600: '#3182ff',
      700: '#1e62db',
      800: '#1849b0',
      900: '#153a8a',
    },
    // Secondary - Purple (Skill/Intelligence)
    secondary: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea',
      700: '#7e22ce',
      800: '#6b21a8',
      900: '#581c87',
    },
    // Accent - Emerald (Success/Progress)
    success: {
      50: '#f0fdf4',
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#145231',
    },
    // Warning - Amber
    warning: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
    // Error - Red
    error: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
    // Neutral - Professional Gray
    neutral: {
      50: '#fafafa',
      100: '#f5f5f5',
      150: '#f0f0f0',
      200: '#e5e5e5',
      300: '#d4d4d4',
      400: '#a3a3a3',
      500: '#737373',
      600: '#525252',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    },
  },

  // Typography System
  typography: {
    // Font families
    fonts: {
      display: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      body: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      mono: '"Menlo", "Monaco", "Courier New", monospace',
    },
    // Sizes
    sizes: {
      xs: '0.75rem', // 12px
      sm: '0.875rem', // 14px
      base: '1rem', // 16px
      lg: '1.125rem', // 18px
      xl: '1.25rem', // 20px
      '2xl': '1.5rem', // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem', // 48px
      '6xl': '3.75rem', // 60px
    },
    // Line heights
    lineHeights: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
      loose: 2,
    },
    // Font weights
    weights: {
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
  },

  // Spacing System
  spacing: {
    0: '0',
    px: '1px',
    0.5: '0.125rem', // 2px
    1: '0.25rem', // 4px
    1.5: '0.375rem', // 6px
    2: '0.5rem', // 8px
    2.5: '0.625rem', // 10px
    3: '0.75rem', // 12px
    3.5: '0.875rem', // 14px
    4: '1rem', // 16px
    5: '1.25rem', // 20px
    6: '1.5rem', // 24px
    7: '1.75rem', // 28px
    8: '2rem', // 32px
    9: '2.25rem', // 36px
    10: '2.5rem', // 40px
    12: '3rem', // 48px
    14: '3.5rem', // 56px
    16: '4rem', // 64px
    20: '5rem', // 80px
    24: '6rem', // 96px
    32: '8rem', // 128px
  },

  // Shadows - Layered depth
  shadows: {
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    base: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    md: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    xl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    
    // Elevated surfaces
    surface: '0 2px 8px rgba(0, 0, 0, 0.08)',
    elevated: '0 8px 24px rgba(0, 0, 0, 0.12)',
    
    // Blue glow (AI theme)
    glow: '0 0 20px rgba(75, 154, 255, 0.3)',
  },

  // Border Radius
  radius: {
    none: '0',
    sm: '0.375rem', // 6px
    base: '0.5rem', // 8px
    md: '0.75rem', // 12px
    lg: '1rem', // 16px
    xl: '1.25rem', // 20px
    '2xl': '1.5rem', // 24px
    full: '9999px',
  },

  // Transitions
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    'extra-slow': '500ms cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Breakpoints
  breakpoints: {
    xs: '390px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1440px',
    '3xl': '1680px',
  },

  // Z-index scale
  zIndex: {
    hide: '-1',
    base: '0',
    dropdown: '10',
    sticky: '20',
    fixed: '30',
    backdrop: '40',
    offcanvas: '50',
    modal: '60',
    notification: '70',
    tooltip: '80',
  },
};

// Color utilities
export const getColor = (path: string) => {
  const keys = path.split('.');
  let value: any = DESIGN_SYSTEM.colors;
  for (const key of keys) {
    value = value[key];
  }
  return value;
};

// CSS Variables for Tailwind integration
export const getCSSVariables = () => {
  const vars: Record<string, string> = {};
  
  // Colors
  Object.entries(DESIGN_SYSTEM.colors).forEach(([colorName, shades]) => {
    if (typeof shades === 'object') {
      Object.entries(shades).forEach(([shade, value]) => {
        vars[`--color-${colorName}-${shade}`] = value;
      });
    }
  });

  // Spacing
  Object.entries(DESIGN_SYSTEM.spacing).forEach(([key, value]) => {
    vars[`--spacing-${key}`] = value;
  });

  // Shadows
  Object.entries(DESIGN_SYSTEM.shadows).forEach(([key, value]) => {
    vars[`--shadow-${key}`] = value;
  });

  // Typography
  Object.entries(DESIGN_SYSTEM.typography.sizes).forEach(([key, value]) => {
    vars[`--size-${key}`] = value;
  });

  return vars;
};