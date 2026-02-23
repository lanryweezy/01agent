import React from 'react';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  padding: 2rem;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  min-height: 100vh;
  color: white;
`;

const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
`;

const Card = styled.div`
  background: rgba(255,255,255,0.1);
  padding: 2rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
`;

const Button = styled.button`
  background: linear-gradient(45deg, #00ff88, #00ccff);
  color: #1a1a1a;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 255, 136, 0.3);
  }
`;

const Link = styled.a`
  color: #00ccff;
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
`;

const QuickActionButton = styled.button`
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  &:hover {
    background: rgba(255,255,255,0.3);
  }
`;

const Dashboard = () => (
  <DashboardContainer>
    <h1>🤖 01Agent Dashboard</h1>
    <DashboardGrid>
      <Card>
        <h3>🎛️ Agent Control</h3>
        <p>Status: <span style={{ color: '#00ff88' }}>Ready</span></p>
        <Button>
          Start Agent
        </Button>
      </Card>

      <Card>
        <h3>📊 Performance</h3>
        <p>CPU: <span style={{ color: '#00ff88' }}>25%</span></p>
        <p>Memory: <span style={{ color: '#00ff88' }}>45%</span></p>
        <p>Tasks: <span style={{ color: '#00ff88' }}>12 completed</span></p>
      </Card>

      <Card>
        <h3>🔧 Backend Status</h3>
        <p>API: <span style={{ color: '#00ff88' }}>Connected</span></p>
        <p>Port: <span style={{ color: '#00ccff' }}>8001</span></p>
        <Link 
          href="http://localhost:8001" 
          target="_blank" 
          rel="noopener noreferrer"
        >
          🔗 Open API
        </Link>
      </Card>

      <Card>
        <h3>🚀 Quick Actions</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <QuickActionButton>
            📸 Take Screenshot
          </QuickActionButton>
          <QuickActionButton>
            🖱️ UI Automation
          </QuickActionButton>
          <QuickActionButton>
            📋 Task Manager
          </QuickActionButton>
        </div>
      </Card>
    </DashboardGrid>

    <div style={{ marginTop: '3rem', textAlign: 'center', opacity: 0.8 }}>
      <p>🎉 Your 01Agent Desktop App is running successfully!</p>
      <p>Backend API: <Link href="http://localhost:8001" target="_blank" rel="noopener noreferrer">http://localhost:8001</Link></p>
      <p>API Docs: <Link href="http://localhost:8001/docs" target="_blank" rel="noopener noreferrer">http://localhost:8001/docs</Link></p>
    </div>
  </DashboardContainer>
);

export default Dashboard;