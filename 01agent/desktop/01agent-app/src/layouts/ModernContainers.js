import styled from 'styled-components';
import theme from '../theme/GlobalTheme';

export const ModernSidePanelContainer = styled.div`
  display: flex;
  height: 100vh;
  width: 100vw;
  background: ${props => props.isDarkMode ? theme.colors.dark.background : theme.colors.light.background};
  color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
  font-family: ${theme.fonts.primary};
  overflow: hidden;
  position: relative;
  
  /* Enhanced backdrop blur effect */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.isDarkMode 
      ? 'radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(0, 255, 136, 0.05) 0%, transparent 50%)'
      : 'radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.05) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(0, 255, 136, 0.03) 0%, transparent 50%)'
    };
    pointer-events: none;
    z-index: 0;
  }
  
  /* Modern scrollbar */
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
    background: ${props => props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
    border-radius: 3px;
  }
  
  *::-webkit-scrollbar-thumb {
    background: ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
    border-radius: 3px;
    transition: background ${theme.transitions.fast};
  }
  
  *::-webkit-scrollbar-thumb:hover {
    background: ${props => props.isDarkMode ? theme.colors.dark.borderLight : theme.colors.light.borderLight};
  }
`;

export const SidePanelSidebar = styled.div`
  width: 320px;
  min-width: 320px;
  background: ${props => props.isDarkMode 
    ? `linear-gradient(180deg, ${theme.colors.dark.surface} 0%, ${theme.colors.dark.background} 100%)`
    : `linear-gradient(180deg, ${theme.colors.light.surface} 0%, ${theme.colors.light.background} 100%)`
  };
  border-right: 1px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 100;
  backdrop-filter: blur(10px);
  
  /* Enhanced glass effect */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.isDarkMode 
      ? 'linear-gradient(135deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 100%)'
      : 'linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%)'
    };
    pointer-events: none;
  }
  
  /* Resize handle */
  &::after {
    content: '';
    position: absolute;
    right: -2px;
    top: 0;
    bottom: 0;
    width: 4px;
    cursor: col-resize;
    background: transparent;
    transition: background ${theme.transitions.fast};
    
    &:hover {
      background: ${props => props.isDarkMode ? theme.colors.primary : theme.colors.primary}40;
    }
  }
`;

export const SidePanelContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: ${props => props.isDarkMode ? theme.colors.dark.background : theme.colors.light.background};
  position: relative;
  z-index: 1;
`;

export const SidePanelHeader = styled.div`
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  border-bottom: 1px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  background: ${props => props.isDarkMode 
    ? `linear-gradient(135deg, ${theme.colors.dark.surface} 0%, ${theme.colors.dark.background} 100%)`
    : `linear-gradient(135deg, ${theme.colors.light.surface} 0%, ${theme.colors.light.background} 100%)`
  };
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 70px;
  backdrop-filter: blur(10px);
  position: relative;
  
  /* Subtle glow effect */
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, ${theme.colors.primary}40, transparent);
  }
`;

export const SidePanelTitle = styled.h1`
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  
  .icon {
    font-size: 24px;
    background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.accent} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

export const SidePanelBody = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0;
`;

export const NavigationList = styled.div`
  padding: 8px 0;
`;

export const NavigationItem = styled.div`
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  font-size: 14px;
  font-weight: 500;
  color: ${props => props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary};
  transition: all ${theme.transitions.fast};
  border-left: 3px solid transparent;
  border-radius: 0 ${theme.radius.md} ${theme.radius.md} 0;
  margin: 2px ${theme.spacing.sm} 2px 0;
  position: relative;
  
  &:hover {
    background: ${props => props.isDarkMode 
      ? `linear-gradient(135deg, ${theme.colors.dark.surfaceHover} 0%, ${theme.colors.primary}10 100%)`
      : `linear-gradient(135deg, ${theme.colors.light.surfaceHover} 0%, ${theme.colors.primary}10 100%)`
    };
    color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
    transform: translateX(4px);
  }
  
  &.active {
    background: ${props => props.isDarkMode 
      ? `linear-gradient(135deg, ${theme.colors.primary}20 0%, ${theme.colors.accent}10 100%)`
      : `linear-gradient(135deg, ${theme.colors.primary}15 0%, ${theme.colors.accent}08 100%)`
    };
    color: ${theme.colors.primary};
    border-left-color: ${theme.colors.primary};
    transform: translateX(4px);
    
    &::after {
      content: '';
      position: absolute;
      right: -1px;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 20px;
      background: linear-gradient(180deg, ${theme.colors.primary} 0%, ${theme.colors.accent} 100%);
      border-radius: 2px 0 0 2px;
    }
  }
  
  .icon {
    width: 18px;
    height: 18px;
    opacity: 0.9;
    transition: transform ${theme.transitions.fast};
  }
  
  &:hover .icon,
  &.active .icon {
    transform: scale(1.1);
  }
`;

export const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    switch (props.status) {
      case 'active': return '#10b981';
      case 'working': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'idle': return '#6b7280';
      default: return '#6b7280';
    }
  }};
  margin-left: auto;
  animation: ${props => props.status === 'working' ? 'pulse 2s infinite' : 'none'};
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

export const PerformanceBar = styled.div`
  margin: ${theme.spacing.md} ${theme.spacing.xl};
  padding: ${theme.spacing.md};
  background: ${props => props.isDarkMode 
    ? `linear-gradient(135deg, ${theme.colors.dark.surface} 0%, ${theme.colors.dark.background} 100%)`
    : `linear-gradient(135deg, ${theme.colors.light.surface} 0%, ${theme.colors.light.background} 100%)`
  };
  border-radius: ${theme.radius.lg};
  border: 1px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  backdrop-filter: blur(10px);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.isDarkMode 
      ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(0, 255, 136, 0.03) 100%)'
      : 'linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(0, 255, 136, 0.02) 100%)'
    };
    border-radius: ${theme.radius.lg};
    pointer-events: none;
  }
`;

export const PerformanceTitle = styled.div`
  font-size: 12px;
  font-weight: 600;
  color: ${props => props.isDarkMode ? '#e1e4e8' : '#586069'};
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const PerformanceMetric = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 13px;
  
  .label {
    color: ${props => props.isDarkMode ? '#e1e4e8' : '#586069'};
  }
  
  .value {
    color: ${props => props.isDarkMode ? '#ffffff' : '#24292e'};
    font-weight: 500;
  }
`;

export const QuickActionButton = styled.button`
  width: 100%;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  margin: ${theme.spacing.xs} 0;
  background: ${props => props.primary 
    ? `linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryLight} 100%)`
    : 'transparent'
  };
  color: ${props => props.primary 
    ? 'white'
    : (props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary)
  };
  border: 1px solid ${props => props.primary 
    ? 'transparent'
    : (props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border)
  };
  border-radius: ${theme.radius.md};
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};
  position: relative;
  overflow: hidden;
  
  &:hover:not(:disabled) {
    background: ${props => props.primary 
      ? `linear-gradient(135deg, ${theme.colors.primaryHover} 0%, ${theme.colors.primary} 100%)`
      : (props.isDarkMode ? theme.colors.dark.surfaceHover : theme.colors.light.surfaceHover)
    };
    transform: translateY(-1px);
    box-shadow: ${props => props.primary ? theme.shadows.glow : theme.shadows.md};
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
  }
  
  .icon {
    width: 16px;
    height: 16px;
    transition: transform ${theme.transitions.fast};
  }
  
  &:hover:not(:disabled) .icon {
    transform: scale(1.1);
  }
  
  /* Ripple effect */
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width 0.3s, height 0.3s;
  }
  
  &:active::after {
    width: 100px;
    height: 100px;
  }
`;

export const OverlayContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${props => props.isDarkMode ? 'rgba(0, 0, 0, 0.9)' : 'rgba(255, 255, 255, 0.95)'};
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

export const Card = styled.div`
  background: ${props => props.isDarkMode ? '#2a2a2a' : '#ffffff'};
  border: 1px solid ${props => props.isDarkMode ? '#404040' : '#e1e4e8'};
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

export const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: ${props => props.isDarkMode ? '#ffffff' : '#24292e'};
  }
`;

export const CardContent = styled.div`
  color: ${props => props.isDarkMode ? '#e1e4e8' : '#586069'};
  font-size: 14px;
  line-height: 1.5;
`;

export const Badge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  background: ${props => {
    switch (props.variant) {
      case 'success': return props.isDarkMode ? '#065f46' : '#d1fae5';
      case 'warning': return props.isDarkMode ? '#92400e' : '#fef3c7';
      case 'error': return props.isDarkMode ? '#991b1b' : '#fee2e2';
      case 'info': return props.isDarkMode ? '#1e40af' : '#dbeafe';
      default: return props.isDarkMode ? '#374151' : '#f3f4f6';
    }
  }};
  
  color: ${props => {
    switch (props.variant) {
      case 'success': return props.isDarkMode ? '#10b981' : '#065f46';
      case 'warning': return props.isDarkMode ? '#f59e0b' : '#92400e';
      case 'error': return props.isDarkMode ? '#ef4444' : '#991b1b';
      case 'info': return props.isDarkMode ? '#3b82f6' : '#1e40af';
      default: return props.isDarkMode ? '#e5e7eb' : '#6b7280';
    }
  }};
`;

export const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: ${props => props.isDarkMode ? '#374151' : '#e5e7eb'};
  border-radius: 2px;
  overflow: hidden;
  margin: 8px 0;
  
  .fill {
    height: 100%;
    background: ${props => {
      if (props.value > 80) return '#ef4444';
      if (props.value > 60) return '#f59e0b';
      return '#10b981';
    }};
    width: ${props => props.value}%;
    transition: width 0.3s ease;
  }
`;

export const Tooltip = styled.div`
  position: absolute;
  background: ${props => props.isDarkMode ? '#1f2937' : '#374151'};
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  pointer-events: none;
  opacity: ${props => props.visible ? 1 : 0};
  transition: opacity 0.15s ease;
`;