import styled from 'styled-components';
import theme from '../../theme/GlobalTheme';

// Enhanced Button Component
export const Button = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};
  padding: ${props => {
    switch (props.size) {
      case 'sm': return '6px 12px';
      case 'lg': return '12px 24px';
      case 'xl': return '16px 32px';
      default: return '8px 16px';
    }
  }};
  font-size: ${props => {
    switch (props.size) {
      case 'sm': return '12px';
      case 'lg': return '16px';
      case 'xl': return '18px';
      default: return '14px';
    }
  }};
  font-weight: 600;
  border-radius: ${theme.radius.md};
  border: none;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  position: relative;
  overflow: hidden;
  
  /* Variant styles */
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryLight} 100%);
          color: white;
          box-shadow: ${theme.shadows.md};
          
          &:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: ${theme.shadows.glow};
          }
          
          &:active {
            transform: translateY(0);
          }
        `;
      case 'secondary':
        return `
          background: transparent;
          color: ${props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
          border: 2px solid ${props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
          
          &:hover:not(:disabled) {
            border-color: ${theme.colors.primary};
            color: ${theme.colors.primary};
            transform: translateY(-1px);
          }
        `;
      case 'accent':
        return `
          background: linear-gradient(135deg, ${theme.colors.accent} 0%, ${theme.colors.accentLight} 100%);
          color: ${theme.colors.dark.background};
          box-shadow: ${theme.shadows.md};
          
          &:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 0 20px ${theme.colors.accent}40;
          }
        `;
      case 'ghost':
        return `
          background: transparent;
          color: ${props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary};
          
          &:hover:not(:disabled) {
            background: ${props.isDarkMode ? theme.colors.dark.surfaceHover : theme.colors.light.surfaceHover};
            color: ${props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
          }
        `;
      default:
        return `
          background: ${props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
          color: ${props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
          border: 1px solid ${props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
          
          &:hover:not(:disabled) {
            background: ${props.isDarkMode ? theme.colors.dark.surfaceHover : theme.colors.light.surfaceHover};
            transform: translateY(-1px);
          }
        `;
    }
  }}
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
  }
  
  /* Loading state */
  ${props => props.loading && `
    pointer-events: none;
    
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  `}
`;

// Enhanced Card Component
export const Card = styled.div`
  background: ${props => props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
  border: 1px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  border-radius: ${theme.radius.lg};
  padding: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.md};
  transition: all ${theme.transitions.fast};
  position: relative;
  overflow: hidden;
  
  ${props => props.hover && `
    &:hover {
      transform: translateY(-2px);
      box-shadow: ${theme.shadows.lg};
      border-color: ${theme.colors.primary};
    }
  `}
  
  ${props => props.glow && `
    box-shadow: 0 0 20px ${theme.colors.primary}20;
  `}
  
  &:last-child {
    margin-bottom: 0;
  }
`;

// Enhanced Input Component
export const Input = styled.input`
  width: 100%;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  font-size: 14px;
  font-family: ${theme.fonts.primary};
  background: ${props => props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
  color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
  border: 2px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  border-radius: ${theme.radius.md};
  transition: all ${theme.transitions.fast};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}20;
  }
  
  &::placeholder {
    color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// Enhanced TextArea Component
export const TextArea = styled.textarea`
  width: 100%;
  padding: ${theme.spacing.md};
  font-size: 14px;
  font-family: ${theme.fonts.primary};
  background: ${props => props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
  color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
  border: 2px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  border-radius: ${theme.radius.md};
  transition: all ${theme.transitions.fast};
  resize: vertical;
  min-height: 100px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}20;
  }
  
  &::placeholder {
    color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// Enhanced Badge Component
export const Badge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: ${theme.radius.full};
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  ${props => {
    switch (props.variant) {
      case 'success':
        return `
          background: ${theme.colors.success}20;
          color: ${theme.colors.success};
          border: 1px solid ${theme.colors.success}40;
        `;
      case 'warning':
        return `
          background: ${theme.colors.warning}20;
          color: ${theme.colors.warning};
          border: 1px solid ${theme.colors.warning}40;
        `;
      case 'error':
        return `
          background: ${theme.colors.error}20;
          color: ${theme.colors.error};
          border: 1px solid ${theme.colors.error}40;
        `;
      case 'info':
        return `
          background: ${theme.colors.info}20;
          color: ${theme.colors.info};
          border: 1px solid ${theme.colors.info}40;
        `;
      case 'primary':
        return `
          background: ${theme.colors.primary}20;
          color: ${theme.colors.primary};
          border: 1px solid ${theme.colors.primary}40;
        `;
      default:
        return `
          background: ${props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
          color: ${props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary};
          border: 1px solid ${props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
        `;
    }
  }}
`;

// Enhanced Progress Bar
export const ProgressBar = styled.div`
  width: 100%;
  height: 6px;
  background: ${props => props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
  border-radius: ${theme.radius.full};
  overflow: hidden;
  position: relative;
  
  .fill {
    height: 100%;
    background: ${props => {
      if (props.value > 80) return theme.colors.error;
      if (props.value > 60) return theme.colors.warning;
      return theme.colors.success;
    }};
    width: ${props => Math.min(100, Math.max(0, props.value || 0))}%;
    transition: width ${theme.transitions.normal};
    border-radius: ${theme.radius.full};
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
      animation: shimmer 2s infinite;
    }
  }
  
  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
`;

// Enhanced Toggle Switch
export const Toggle = styled.label`
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  
  input {
    display: none;
  }
  
  .switch {
    position: relative;
    width: 44px;
    height: 24px;
    background: ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
    border-radius: ${theme.radius.full};
    transition: background ${theme.transitions.fast};
    
    &::after {
      content: '';
      position: absolute;
      top: 2px;
      left: 2px;
      width: 20px;
      height: 20px;
      background: white;
      border-radius: ${theme.radius.full};
      transition: transform ${theme.transitions.fast};
      box-shadow: ${theme.shadows.sm};
    }
  }
  
  input:checked + .switch {
    background: ${theme.colors.primary};
    
    &::after {
      transform: translateX(20px);
    }
  }
  
  .label {
    margin-left: ${theme.spacing.sm};
    font-size: 14px;
    color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
  }
`;

// Enhanced Tooltip
export const Tooltip = styled.div`
  position: absolute;
  background: ${props => props.isDarkMode ? theme.colors.light.text : theme.colors.dark.surface};
  color: ${props => props.isDarkMode ? theme.colors.light.background : theme.colors.dark.text};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.radius.md};
  font-size: 12px;
  white-space: nowrap;
  z-index: ${theme.zIndex.tooltip};
  pointer-events: none;
  opacity: ${props => props.visible ? 1 : 0};
  transform: ${props => props.visible ? 'translateY(0)' : 'translateY(4px)'};
  transition: all ${theme.transitions.fast};
  box-shadow: ${theme.shadows.lg};
  
  &::before {
    content: '';
    position: absolute;
    top: -4px;
    left: 50%;
    transform: translateX(-50%);
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid ${props => props.isDarkMode ? theme.colors.light.text : theme.colors.dark.surface};
  }
`;

// Enhanced Modal Overlay
export const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: ${theme.zIndex.modal};
  opacity: ${props => props.visible ? 1 : 0};
  visibility: ${props => props.visible ? 'visible' : 'hidden'};
  transition: all ${theme.transitions.normal};
`;

// Enhanced Modal Content
export const ModalContent = styled.div`
  background: ${props => props.isDarkMode ? theme.colors.dark.surface : theme.colors.light.surface};
  border-radius: ${theme.radius.xl};
  padding: ${theme.spacing.xl};
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
  box-shadow: ${theme.shadows.xl};
  transform: ${props => props.visible ? 'scale(1)' : 'scale(0.95)'};
  transition: transform ${theme.transitions.normal};
`;

// Enhanced Loading Spinner
export const LoadingSpinner = styled.div`
  width: ${props => props.size || '24px'};
  height: ${props => props.size || '24px'};
  border: 2px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  border-top: 2px solid ${theme.colors.primary};
  border-radius: ${theme.radius.full};
  animation: spin 1s linear infinite;
  
  ${props => props.center && `
    margin: ${theme.spacing.lg} auto;
    display: block;
  `}
`;

// Enhanced Status Indicator
export const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: ${theme.radius.full};
  background: ${props => {
    switch (props.status) {
      case 'active': return theme.colors.success;
      case 'working': return theme.colors.warning;
      case 'error': return theme.colors.error;
      case 'idle': return theme.colors.dark.textMuted;
      default: return theme.colors.dark.textMuted;
    }
  }};
  
  ${props => props.status === 'working' && `
    animation: pulse 2s infinite;
  `}
  
  ${props => props.withLabel && `
    position: relative;
    
    &::after {
      content: '${props.status}';
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 12px;
      color: ${props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary};
      text-transform: capitalize;
    }
  `}
`;

export default {
  Button,
  Card,
  Input,
  TextArea,
  Badge,
  ProgressBar,
  Toggle,
  Tooltip,
  ModalOverlay,
  ModalContent,
  LoadingSpinner,
  StatusIndicator
};