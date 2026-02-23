import styled, { createGlobalStyle } from 'styled-components';

// Global theme configuration
export const theme = {
  colors: {
    // Primary brand colors
    primary: '#667eea',
    primaryHover: '#5a6fd8',
    primaryLight: '#8b9df0',
    
    // Accent colors
    accent: '#00ff88',
    accentHover: '#00e67a',
    accentLight: '#33ff99',
    
    // Status colors
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    
    // Dark theme
    dark: {
      background: '#0f0f0f',
      surface: '#1a1a1a',
      surfaceHover: '#252525',
      border: '#333333',
      borderLight: '#404040',
      text: '#ffffff',
      textSecondary: '#e1e4e8',
      textMuted: '#9ca3af',
      textDisabled: '#6b7280'
    },
    
    // Light theme
    light: {
      background: '#ffffff',
      surface: '#f8f9fa',
      surfaceHover: '#f1f3f4',
      border: '#e1e4e8',
      borderLight: '#f0f0f0',
      text: '#24292e',
      textSecondary: '#586069',
      textMuted: '#6b7280',
      textDisabled: '#9ca3af'
    }
  },
  
  // Typography
  fonts: {
    primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    mono: 'Monaco, Consolas, "Courier New", monospace'
  },
  
  // Spacing
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px'
  },
  
  // Border radius
  radius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '50%'
  },
  
  // Shadows
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px rgba(0, 0, 0, 0.1)',
    glow: '0 0 20px rgba(102, 126, 234, 0.3)'
  },
  
  // Transitions
  transitions: {
    fast: '0.15s ease',
    normal: '0.3s ease',
    slow: '0.5s ease'
  },
  
  // Z-index layers
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060
  }
};

// Global styles
export const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  html {
    scroll-behavior: smooth;
  }
  
  body {
    font-family: ${theme.fonts.primary};
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: hidden;
  }
  
  /* Custom scrollbar */
  * {
    scrollbar-width: thin;
    scrollbar-color: ${props => props.isDarkMode 
      ? `${theme.colors.dark.border} ${theme.colors.dark.surface}` 
      : `${theme.colors.light.border} ${theme.colors.light.surface}`
    };
  }
  
  *::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  
  *::-webkit-scrollbar-track {
    background: ${props => props.isDarkMode 
      ? theme.colors.dark.surface 
      : theme.colors.light.surface
    };
  }
  
  *::-webkit-scrollbar-thumb {
    background: ${props => props.isDarkMode 
      ? theme.colors.dark.border 
      : theme.colors.light.border
    };
    border-radius: 3px;
  }
  
  *::-webkit-scrollbar-thumb:hover {
    background: ${props => props.isDarkMode 
      ? theme.colors.dark.borderLight 
      : theme.colors.light.borderLight
    };
  }
  
  /* Focus styles */
  *:focus {
    outline: 2px solid ${theme.colors.primary};
    outline-offset: 2px;
  }
  
  /* Selection styles */
  ::selection {
    background: ${theme.colors.primary};
    color: white;
  }
  
  /* Animations */
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes slideIn {
    from { transform: translateY(-10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .animate-fadeIn {
    animation: fadeIn 0.3s ease;
  }
  
  .animate-slideIn {
    animation: slideIn 0.3s ease;
  }
  
  .animate-pulse {
    animation: pulse 2s infinite;
  }
  
  .animate-spin {
    animation: spin 1s linear infinite;
  }
`;

// Theme provider wrapper
export const AppTheme = styled.div`
  background: ${props => props.isDarkMode 
    ? theme.colors.dark.background 
    : theme.colors.light.background
  };
  color: ${props => props.isDarkMode 
    ? theme.colors.dark.text 
    : theme.colors.light.text
  };
  min-height: 100vh;
  transition: background-color ${theme.transitions.normal}, color ${theme.transitions.normal};
`;

export default theme;