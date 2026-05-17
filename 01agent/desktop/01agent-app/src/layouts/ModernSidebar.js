import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  SidePanelSidebar,
  SidePanelHeader,
  SidePanelTitle,
  SidePanelBody,
  NavigationList,
  NavigationItem,
  StatusIndicator,
  PerformanceBar,
  PerformanceTitle,
  PerformanceMetric,
  QuickActionButton,
  Badge
} from './ModernContainers';
import { setDarkMode } from '../store';
// import theme from '../theme/GlobalTheme';

// Enhanced Icons with better visual hierarchy
const Icons = {
  home: '🏠',
  threads: '💬',
  settings: '⚙️',
  performance: '📊',
  status: '🔍',
  darkMode: '🌙',
  lightMode: '☀️',
  play: '▶️',
  stop: '⏹️',
  refresh: '🔄',
  logo: '🤖',
  lightning: '⚡',
  brain: '🧠',
  rocket: '🚀'
};

const ModernSidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  
  const isDarkMode = useSelector(state => state.isDarkMode);
  const user = useSelector(state => state.user);
  
  const [agentStatus, setAgentStatus] = useState('idle');
  const [performanceData, setPerformanceData] = useState({
    cpu: 0,
    memory: 0,
    tasks: 0,
    successRate: 0
  });
  const [isAgentRunning, setIsAgentRunning] = useState(false);

  useEffect(() => {
    // Listen for agent status updates
    if (window.electronAPI?.onAIAgentLaunch) {
      window.electronAPI.onAIAgentLaunch(() => {
        setIsAgentRunning(true);
        setAgentStatus('working');
      });
    }

    if (window.electronAPI?.onAIAgentExit) {
      window.electronAPI.onAIAgentExit(() => {
        setIsAgentRunning(false);
        setAgentStatus('idle');
      });
    }

    // Simulate performance data updates
    const interval = setInterval(() => {
      setPerformanceData(() => ({
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        tasks: Math.floor(Math.random() * 50),
        successRate: 85 + Math.random() * 15
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const navigationItems = React.useMemo(() => [
    { path: '/', label: 'Home', icon: Icons.home },
    { path: '/threads', label: 'Threads', icon: Icons.threads },
    { path: '/performance', label: 'Performance', icon: Icons.performance },
    { path: '/status', label: 'Agent Status', icon: Icons.status },
    { path: '/settings', label: 'Settings', icon: Icons.settings }
  ], []);

  const handleNavigation = React.useCallback((path) => {
    navigate(path);
  }, [navigate]);

  const toggleDarkMode = async () => {
    const newDarkMode = !isDarkMode;
    dispatch(setDarkMode(newDarkMode));
    if (window.electronAPI?.setDarkMode) {
      window.electronAPI.setDarkMode(newDarkMode);
    }
  };

  const startAgent = async () => {
    if (window.electronAPI?.launchAIAgent) {
      const baseURL = process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS;
      const threadId = 'default'; // You might want to get this from state
      const backgroundMode = false;
      
      window.electronAPI.launchAIAgent(baseURL, threadId, backgroundMode);
    }
  };

  const stopAgent = async () => {
    if (window.electronAPI?.stopAIAgent) {
      window.electronAPI.stopAIAgent();
    }
  };

  const refreshPerformance = () => {
    // Trigger performance data refresh
    setPerformanceData(prev => ({
      ...prev,
      cpu: Math.random() * 100,
      memory: Math.random() * 100
    }));
  };

  // ⚡ Bolt: Memoize navigation items mapping to prevent O(N) VDOM node recreation on frequent telemetry updates (every 2 seconds)
  const memoizedNavigationItems = useMemo(() => {
    return navigationItems.map((item) => (
      <NavigationItem
        key={item.path}
        className={location.pathname === item.path ? 'active' : ''}
        onClick={() => handleNavigation(item.path)}
        isDarkMode={isDarkMode}
      >
        <span className="icon">{item.icon}</span>
        {item.label}
        <StatusIndicator status={agentStatus} />
      </NavigationItem>
    ));
  }, [location.pathname, isDarkMode, agentStatus, handleNavigation, navigationItems]);

  return (
    <SidePanelSidebar isDarkMode={isDarkMode}>
      <SidePanelHeader isDarkMode={isDarkMode}>
        <SidePanelTitle isDarkMode={isDarkMode}>
          <span className="icon">{Icons.logo}</span>
          01Agent
          <Badge variant={agentStatus === 'working' ? 'success' : agentStatus === 'error' ? 'error' : 'default'} isDarkMode={isDarkMode}>
            {agentStatus}
          </Badge>
        </SidePanelTitle>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={toggleDarkMode}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              fontSize: '16px',
              padding: '4px'
            }}
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDarkMode ? Icons.lightMode : Icons.darkMode}
          </button>
        </div>
      </SidePanelHeader>

      <SidePanelBody>
        <NavigationList>
          {memoizedNavigationItems}
        </NavigationList>

        <PerformanceBar isDarkMode={isDarkMode}>
          <PerformanceTitle isDarkMode={isDarkMode}>
            Quick Stats
          </PerformanceTitle>
          
          <PerformanceMetric isDarkMode={isDarkMode}>
            <span className="label">CPU Usage</span>
            <span className="value">{performanceData.cpu.toFixed(1)}%</span>
          </PerformanceMetric>
          
          <PerformanceMetric isDarkMode={isDarkMode}>
            <span className="label">Memory</span>
            <span className="value">{performanceData.memory.toFixed(1)}%</span>
          </PerformanceMetric>
          
          <PerformanceMetric isDarkMode={isDarkMode}>
            <span className="label">Tasks</span>
            <span className="value">{performanceData.tasks}</span>
          </PerformanceMetric>
          
          <PerformanceMetric isDarkMode={isDarkMode}>
            <span className="label">Success Rate</span>
            <span className="value">{performanceData.successRate.toFixed(1)}%</span>
          </PerformanceMetric>
        </PerformanceBar>

        <div style={{ padding: '16px 20px' }}>
          <PerformanceTitle isDarkMode={isDarkMode}>
            Quick Actions
          </PerformanceTitle>
          
          {!isAgentRunning ? (
            <QuickActionButton
              primary
              isDarkMode={isDarkMode}
              onClick={startAgent}
            >
              <span className="icon">{Icons.play}</span>
              Start Agent
            </QuickActionButton>
          ) : (
            <QuickActionButton
              isDarkMode={isDarkMode}
              onClick={stopAgent}
            >
              <span className="icon">{Icons.stop}</span>
              Stop Agent
            </QuickActionButton>
          )}
          
          <QuickActionButton
            isDarkMode={isDarkMode}
            onClick={refreshPerformance}
          >
            <span className="icon">{Icons.refresh}</span>
            Refresh Stats
          </QuickActionButton>
        </div>

        {user && (
          <div style={{ 
            padding: '16px 20px', 
            marginTop: 'auto',
            borderTop: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`
          }}>
            <PerformanceTitle isDarkMode={isDarkMode}>
              User
            </PerformanceTitle>
            <div style={{ 
              fontSize: '13px', 
              color: isDarkMode ? '#e1e4e8' : '#586069',
              marginBottom: '4px'
            }}>
              {user.name}
            </div>
            <div style={{ 
              fontSize: '12px', 
              color: isDarkMode ? '#9ca3af' : '#6b7280'
            }}>
              {user.email}
            </div>
          </div>
        )}
      </SidePanelBody>
    </SidePanelSidebar>
  );
};

export default ModernSidebar;