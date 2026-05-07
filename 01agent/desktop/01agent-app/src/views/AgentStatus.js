import React, { useState, useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import {
  SidePanelContent,
  SidePanelHeader,
  SidePanelTitle,
  SidePanelBody,
  Card,
  CardHeader,
  CardContent,
  QuickActionButton,
  Badge,
  ProgressBar
} from '../layouts/ModernContainers';

const AgentStatus = () => {
  const isDarkMode = useSelector(state => state.isDarkMode);
  
  const [agentStatus, setAgentStatus] = useState({
    isRunning: false,
    currentTask: null,
    strategy: 'speed_priority',
    uptime: 0,
    tasksCompleted: 0,
    tasksInQueue: 0,
    lastError: null,
    systemHealth: {
      cpu: 0,
      memory: 0,
      disk: 0,
      network: 0
    },
    components: {
      smartExecutor: 'active',
      terminalController: 'active',
      backgroundExecutor: 'active',
      fastUIDetector: 'active',
      performanceOptimizer: 'active',
      configManager: 'active'
    },
    logs: []
  });

  const [selectedLogLevel, setSelectedLogLevel] = useState('all');
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    // Listen for agent status updates
    if (window.electronAPI?.onAIAgentLaunch) {
      window.electronAPI.onAIAgentLaunch((threadId) => {
        setAgentStatus(prev => ({
          ...prev,
          isRunning: true,
          currentTask: `Thread ${threadId}`,
          uptime: 0
        }));
        addLog('info', `Agent started with thread ${threadId}`);
      });
    }

    if (window.electronAPI?.onAIAgentExit) {
      window.electronAPI.onAIAgentExit(() => {
        setAgentStatus(prev => ({
          ...prev,
          isRunning: false,
          currentTask: null
        }));
        addLog('info', 'Agent stopped');
      });
    }

    // Simulate status updates
    const interval = setInterval(() => {
      updateAgentStatus();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const updateAgentStatus = () => {
    setAgentStatus(prev => ({
      ...prev,
      uptime: prev.isRunning ? prev.uptime + 2 : 0,
      tasksCompleted: prev.isRunning ? prev.tasksCompleted + Math.floor(Math.random() * 2) : prev.tasksCompleted,
      tasksInQueue: Math.floor(Math.random() * 5),
      systemHealth: {
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        disk: Math.random() * 100,
        network: Math.random() * 100
      }
    }));

    // Occasionally add random logs
    if (Math.random() < 0.3) {
      const logTypes = ['info', 'warning', 'error'];
      const messages = [
        'Task executed successfully',
        'Screenshot captured',
        'Terminal command completed',
        'Background script finished',
        'UI element detected',
        'Performance optimization applied'
      ];
      
      addLog(
        logTypes[Math.floor(Math.random() * logTypes.length)],
        messages[Math.floor(Math.random() * messages.length)]
      );
    }
  };

  const addLog = (level, message) => {
    const newLog = {
      id: Date.now(),
      timestamp: new Date(),
      level,
      message
    };

    setAgentStatus(prev => ({
      ...prev,
      logs: [...prev.logs.slice(-99), newLog] // Keep last 100 logs
    }));
  };

  const startAgent = async () => {
    if (window.electronAPI?.launchAIAgent) {
      const baseURL = process.env.REACT_APP_PROTOCOL + '://' + process.env.REACT_APP_DNS;
      const threadId = 'status-monitor';
      const backgroundMode = false;
      
      window.electronAPI.launchAIAgent(baseURL, threadId, backgroundMode);
    }
  };

  const stopAgent = async () => {
    if (window.electronAPI?.stopAIAgent) {
      window.electronAPI.stopAIAgent();
    }
  };

  const restartAgent = async () => {
    await stopAgent();
    setTimeout(startAgent, 2000);
  };

  const clearLogs = () => {
    setAgentStatus(prev => ({
      ...prev,
      logs: []
    }));
  };

  const exportLogs = () => {
    const logsText = agentStatus.logs
      .map(log => `[${log.timestamp.toISOString()}] ${log.level.toUpperCase()}: ${log.message}`)
      .join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `01agent-logs-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getComponentStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'inactive': return 'default';
      default: return 'default';
    }
  };



  // ⚡ Bolt: Memoize the log list to prevent O(N) VDOM node recreation on every frequent state change (like system health metrics)
  const memoizedLogElements = useMemo(() => {
    const getLogLevelColor = (level) => {
      switch (level) {
        case 'error': return '#ef4444';
        case 'warning': return '#f59e0b';
        case 'info': return '#3b82f6';
        default: return isDarkMode ? '#e1e4e8' : '#586069';
      }
    };

    const filteredLogs = agentStatus.logs.filter(log =>
      selectedLogLevel === 'all' || log.level === selectedLogLevel
    );

    if (filteredLogs.length === 0) {
      return (
        <div style={{
          color: isDarkMode ? '#9ca3af' : '#6b7280',
          textAlign: 'center',
          padding: '20px'
        }}>
          No logs available
        </div>
      );
    }

    return filteredLogs.map(log => (
      <div key={log.id} style={{ marginBottom: '4px' }}>
        <span style={{ color: isDarkMode ? '#9ca3af' : '#6b7280' }}>
          [{log.timestamp.toLocaleTimeString()}]
        </span>
        {' '}
        <span style={{
          color: getLogLevelColor(log.level),
          fontWeight: '600',
          textTransform: 'uppercase'
        }}>
          {log.level}:
        </span>
        {' '}
        <span style={{ color: isDarkMode ? '#e1e4e8' : '#24292e' }}>
          {log.message}
        </span>
      </div>
    ));
  }, [isDarkMode, agentStatus.logs, selectedLogLevel]);

  // ⚡ Bolt: Memoize system health mapping to prevent O(N) VDOM node recreation on frequent telemetry updates
  const memoizedSystemHealth = useMemo(() => (
    Object.entries(agentStatus.systemHealth).map(([metric, value]) => (
      <div key={metric}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '4px'
        }}>
          <span style={{
            fontSize: '12px',
            color: isDarkMode ? '#9ca3af' : '#6b7280',
            textTransform: 'capitalize'
          }}>
            {metric}
          </span>
          <span style={{ fontSize: '12px', fontWeight: '600' }}>
            {value.toFixed(1)}%
          </span>
        </div>
        <ProgressBar isDarkMode={isDarkMode} value={value}>
          <div className="fill"></div>
        </ProgressBar>
      </div>
    ))
  ), [isDarkMode, agentStatus.systemHealth]);

  // ⚡ Bolt: Memoize components mapping to prevent O(N) VDOM node recreation on frequent telemetry updates
  const memoizedComponents = useMemo(() => (
    Object.entries(agentStatus.components).map(([component, status]) => (
      <div key={component} style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 12px',
        border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
        borderRadius: '4px',
        background: isDarkMode ? '#2a2a2a' : '#f8f9fa'
      }}>
        <span style={{
          fontSize: '13px',
          fontWeight: '500',
          textTransform: 'capitalize'
        }}>
          {component.replace(/([A-Z])/g, ' $1').trim()}
        </span>
        <Badge variant={getComponentStatusColor(status)} isDarkMode={isDarkMode}>
          {status}
        </Badge>
      </div>
    ))
  ), [isDarkMode, agentStatus.components]);

  return (
    <SidePanelContent>
      <SidePanelHeader isDarkMode={isDarkMode}>
        <SidePanelTitle isDarkMode={isDarkMode}>
          🔍 Agent Status
        </SidePanelTitle>
        <Badge variant={agentStatus.isRunning ? 'success' : 'default'} isDarkMode={isDarkMode}>
          {agentStatus.isRunning ? 'Running' : 'Stopped'}
        </Badge>
      </SidePanelHeader>

      <SidePanelBody>
        <div style={{ padding: '20px' }}>
          
          {/* Agent Overview */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Agent Overview</h3>
              <div style={{ display: 'flex', gap: '8px' }}>
                {!agentStatus.isRunning ? (
                  <QuickActionButton
                    primary
                    isDarkMode={isDarkMode}
                    onClick={startAgent}
                  >
                    ▶️ Start Agent
                  </QuickActionButton>
                ) : (
                  <>
                    <QuickActionButton
                      isDarkMode={isDarkMode}
                      onClick={stopAgent}
                    >
                      ⏹️ Stop
                    </QuickActionButton>
                    <QuickActionButton
                      isDarkMode={isDarkMode}
                      onClick={restartAgent}
                    >
                      🔄 Restart
                    </QuickActionButton>
                  </>
                )}
              </div>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                
                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Status
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '600' }}>
                    {agentStatus.isRunning ? '🟢 Running' : '🔴 Stopped'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Current Task
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '600' }}>
                    {agentStatus.currentTask || 'None'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Strategy
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '600', textTransform: 'capitalize' }}>
                    {agentStatus.strategy.replace('_', ' ')}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Uptime
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '600' }}>
                    {formatUptime(agentStatus.uptime)}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Tasks Completed
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#10b981' }}>
                    {agentStatus.tasksCompleted}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Tasks in Queue
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#f59e0b' }}>
                    {agentStatus.tasksInQueue}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Health */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>System Health</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                
                {memoizedSystemHealth}
              </div>
            </CardContent>
          </Card>

          {/* Component Status */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Component Status</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '12px' }}>
                {memoizedComponents}
              </div>
            </CardContent>
          </Card>

          {/* Logs */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Agent Logs</h3>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <select
                  value={selectedLogLevel}
                  onChange={(e) => setSelectedLogLevel(e.target.value)}
                  style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
                    background: isDarkMode ? '#2a2a2a' : '#ffffff',
                    color: isDarkMode ? '#ffffff' : '#24292e',
                    fontSize: '12px'
                  }}
                >
                  <option value="all">All Levels</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                </select>
                
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={clearLogs}
                  style={{ fontSize: '12px', padding: '4px 8px' }}
                >
                  🗑️ Clear
                </QuickActionButton>
                
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={exportLogs}
                  style={{ fontSize: '12px', padding: '4px 8px' }}
                >
                  📄 Export
                </QuickActionButton>
              </div>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{
                height: '300px',
                overflow: 'auto',
                background: isDarkMode ? '#1a1a1a' : '#f8f9fa',
                border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
                borderRadius: '4px',
                padding: '8px',
                fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                fontSize: '12px'
              }}>
                {memoizedLogElements}
              </div>
            </CardContent>
          </Card>
        </div>
      </SidePanelBody>
    </SidePanelContent>
  );
};

export default AgentStatus;