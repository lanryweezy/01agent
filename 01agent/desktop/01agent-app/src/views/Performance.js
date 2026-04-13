import React, { useState, useEffect } from 'react';
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

const Performance = () => {
  const isDarkMode = useSelector(state => state.isDarkMode);
  
  const [performanceData, setPerformanceData] = useState({
    realTime: {
      cpu: 0,
      memory: 0,
      tasks: 0,
      successRate: 0,
      avgExecutionTime: 0,
      status: 'idle'
    },
    methods: {
      terminal: { count: 0, successRate: 0, avgTime: 0 },
      gui: { count: 0, successRate: 0, avgTime: 0 },
      background: { count: 0, successRate: 0, avgTime: 0 },
      smart: { count: 0, successRate: 0, avgTime: 0 }
    },
    history: [],
    recommendations: []
  });

  const [timeRange, setTimeRange] = useState('1h');
  const [isLoading, setIsLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadPerformanceData();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(loadPerformanceData, 5000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [timeRange, autoRefresh]);

  const loadPerformanceData = async () => {
    try {
      // Simulate API call to get performance data
      // In real implementation, this would call your backend
      const mockData = {
        realTime: {
          cpu: Math.random() * 100,
          memory: Math.random() * 100,
          tasks: Math.floor(Math.random() * 50),
          successRate: 85 + Math.random() * 15,
          avgExecutionTime: 1 + Math.random() * 3,
          status: ['idle', 'working', 'optimizing'][Math.floor(Math.random() * 3)]
        },
        methods: {
          terminal: { 
            count: Math.floor(Math.random() * 100), 
            successRate: 90 + Math.random() * 10, 
            avgTime: 0.5 + Math.random() * 1 
          },
          gui: { 
            count: Math.floor(Math.random() * 50), 
            successRate: 80 + Math.random() * 15, 
            avgTime: 2 + Math.random() * 2 
          },
          background: { 
            count: Math.floor(Math.random() * 30), 
            successRate: 95 + Math.random() * 5, 
            avgTime: 3 + Math.random() * 5 
          },
          smart: { 
            count: Math.floor(Math.random() * 80), 
            successRate: 88 + Math.random() * 12, 
            avgTime: 1 + Math.random() * 2 
          }
        },
        history: generateMockHistory(),
        recommendations: generateMockRecommendations(),
        executionStream: [
          { time: '12:00:01', action: 'Capture Screenshot', status: 'success' },
          { time: '12:00:02', action: 'Vision Reasoning (Claude 3.7)', status: 'working' },
          { time: '12:00:05', action: 'Execute: Click Button', status: 'pending' },
        ]
      };
      
      setPerformanceData(mockData);
    } catch (error) {
      console.error('Failed to load performance data:', error);
    }
  };

  const generateMockHistory = () => {
    const history = [];
    const now = Date.now();
    const points = timeRange === '1h' ? 12 : timeRange === '24h' ? 24 : 7;
    const interval = timeRange === '1h' ? 5 * 60 * 1000 : timeRange === '24h' ? 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
    
    for (let i = points; i >= 0; i--) {
      history.push({
        timestamp: now - (i * interval),
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        tasks: Math.floor(Math.random() * 20),
        successRate: 80 + Math.random() * 20
      });
    }
    
    return history;
  };

  const generateMockRecommendations = () => {
    const recommendations = [
      'Consider switching to speed_priority strategy for better performance',
      'Memory usage is optimal - no action needed',
      'Terminal execution method showing excellent results',
      'Screenshot quality can be reduced to improve speed'
    ];
    
    return recommendations.slice(0, Math.floor(Math.random() * 4) + 1);
  };

  const exportReport = async () => {
    setIsLoading(true);
    try {
      // Simulate export
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In real implementation, this would generate and download a report
      const reportData = {
        timestamp: new Date().toISOString(),
        performanceData,
        timeRange
      };
      
      const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `01agent-performance-report-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export report:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'working': return 'success';
      case 'optimizing': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const formatTime = (seconds) => {
    return `${seconds.toFixed(2)}s`;
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`;
  };

  return (
    <SidePanelContent>
      <SidePanelHeader isDarkMode={isDarkMode}>
        <SidePanelTitle isDarkMode={isDarkMode}>
          📊 Performance Dashboard
        </SidePanelTitle>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            style={{
              padding: '4px 8px',
              borderRadius: '4px',
              border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
              background: isDarkMode ? '#2a2a2a' : '#ffffff',
              color: isDarkMode ? '#ffffff' : '#24292e',
              fontSize: '12px'
            }}
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
          <Badge variant={getStatusColor(performanceData.realTime.status)} isDarkMode={isDarkMode}>
            {performanceData.realTime.status}
          </Badge>
        </div>
      </SidePanelHeader>

      <SidePanelBody>
        <div style={{ padding: '20px' }}>
          
          {/* Real-time Metrics */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Real-time Metrics</h3>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  style={{
                    background: 'transparent',
                    border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
                    color: isDarkMode ? '#e1e4e8' : '#586069',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                >
                  {autoRefresh ? '⏸️ Pause' : '▶️ Resume'}
                </button>
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={loadPerformanceData}
                  style={{ fontSize: '12px', padding: '4px 8px' }}
                >
                  🔄 Refresh
                </QuickActionButton>
              </div>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                
                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    CPU Usage
                  </div>
                  <ProgressBar isDarkMode={isDarkMode} value={performanceData.realTime.cpu}>
                    <div className="fill"></div>
                  </ProgressBar>
                  <div style={{ fontSize: '14px', fontWeight: '600' }}>
                    {formatPercentage(performanceData.realTime.cpu)}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Memory Usage
                  </div>
                  <ProgressBar isDarkMode={isDarkMode} value={performanceData.realTime.memory}>
                    <div className="fill"></div>
                  </ProgressBar>
                  <div style={{ fontSize: '14px', fontWeight: '600' }}>
                    {formatPercentage(performanceData.realTime.memory)}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Active Tasks
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: '600', color: isDarkMode ? '#60a5fa' : '#1976d2' }}>
                    {performanceData.realTime.tasks}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Success Rate
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: '600', color: '#10b981' }}>
                    {formatPercentage(performanceData.realTime.successRate)}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', marginBottom: '4px' }}>
                    Avg Execution Time
                  </div>
                  <div style={{ fontSize: '24px', fontWeight: '600', color: isDarkMode ? '#f59e0b' : '#f57c00' }}>
                    {formatTime(performanceData.realTime.avgExecutionTime)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Method Performance */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Execution Method Performance</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
                {Object.entries(performanceData.methods).map(([method, data]) => (
                  <div key={method} style={{
                    padding: '12px',
                    border: `1px solid ${isDarkMode ? '#404040' : '#e1e4e8'}`,
                    borderRadius: '6px',
                    background: isDarkMode ? '#2a2a2a' : '#f8f9fa'
                  }}>
                    <div style={{ 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      marginBottom: '8px',
                      textTransform: 'capitalize',
                      color: isDarkMode ? '#ffffff' : '#24292e'
                    }}>
                      {method} Method
                    </div>
                    
                    <div style={{ fontSize: '12px', marginBottom: '4px' }}>
                      <span style={{ color: isDarkMode ? '#9ca3af' : '#6b7280' }}>Tasks: </span>
                      <span style={{ fontWeight: '500' }}>{data.count}</span>
                    </div>
                    
                    <div style={{ fontSize: '12px', marginBottom: '4px' }}>
                      <span style={{ color: isDarkMode ? '#9ca3af' : '#6b7280' }}>Success Rate: </span>
                      <span style={{ fontWeight: '500', color: '#10b981' }}>
                        {formatPercentage(data.successRate)}
                      </span>
                    </div>
                    
                    <div style={{ fontSize: '12px' }}>
                      <span style={{ color: isDarkMode ? '#9ca3af' : '#6b7280' }}>Avg Time: </span>
                      <span style={{ fontWeight: '500' }}>{formatTime(data.avgTime)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recommendations */}
          {performanceData.recommendations.length > 0 && (
            <Card isDarkMode={isDarkMode}>
              <CardHeader isDarkMode={isDarkMode}>
                <h3>Performance Recommendations</h3>
              </CardHeader>
              <CardContent isDarkMode={isDarkMode}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {performanceData.recommendations.map((recommendation, index) => (
                    <div key={index} style={{
                      padding: '8px 12px',
                      background: isDarkMode ? '#1f2937' : '#e3f2fd',
                      border: `1px solid ${isDarkMode ? '#374151' : '#bbdefb'}`,
                      borderRadius: '4px',
                      fontSize: '13px',
                      color: isDarkMode ? '#e1e4e8' : '#1565c0'
                    }}>
                      💡 {recommendation}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Export and Actions */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Actions</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={exportReport}
                  disabled={isLoading}
                >
                  {isLoading ? '📊 Exporting...' : '📊 Export Report'}
                </QuickActionButton>
                
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={() => setPerformanceData(prev => ({ ...prev, history: [] }))}
                >
                  🗑️ Clear History
                </QuickActionButton>
                
                <QuickActionButton
                  isDarkMode={isDarkMode}
                  onClick={loadPerformanceData}
                >
                  🔄 Refresh Data
                </QuickActionButton>
              </div>
            </CardContent>
          </Card>

          {/* Execution Stream */}
          <Card isDarkMode={isDarkMode}>
            <CardHeader isDarkMode={isDarkMode}>
              <h3>Live Execution Stream</h3>
            </CardHeader>
            <CardContent isDarkMode={isDarkMode}>
              <div style={{
                fontFamily: 'monospace',
                background: isDarkMode ? '#1a1a1a' : '#f0f0f0',
                padding: '10px',
                borderRadius: '4px',
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {performanceData.executionStream?.map((item, i) => (
                  <div key={i} style={{ marginBottom: '4px', display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#888' }}>[{item.time}]</span>
                    <span style={{ flex: 1, marginLeft: '10px' }}>{item.action}</span>
                    <Badge variant={item.status === 'success' ? 'success' : item.status === 'working' ? 'warning' : 'default'} isDarkMode={isDarkMode}>
                      {item.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </SidePanelBody>
    </SidePanelContent>
  );
};

export default Performance;