import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setAccessToken, setUser } from '../store';
import styled from 'styled-components';

const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: 2rem;
`;

const LoginCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 400px;
  width: 100%;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #00ff88, #00ccff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  margin-bottom: 2rem;
  opacity: 0.9;
`;

const DemoButton = styled.button`
  background: linear-gradient(45deg, #00ff88, #00ccff);
  color: #1a1a1a;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0.5rem;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 255, 136, 0.3);
  }
`;

const InfoText = styled.div`
  margin-top: 2rem;
  font-size: 0.9rem;
  opacity: 0.8;
  line-height: 1.5;
`;

function SimpleLogin() {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleDemoLogin = () => {
    // Set demo user and token
    dispatch(setAccessToken('demo-token-123'));
    dispatch(setUser({
      id: 'demo-user',
      name: 'Demo User',
      email: 'demo@01agent.com'
    }));
    
    // Navigate to home
    navigate('/');
  };

  return (
    <LoginContainer>
      <LoginCard>
        <Title>🤖 01Agent</Title>
        <Subtitle>AI Desktop Agent</Subtitle>
        
        <DemoButton onClick={handleDemoLogin}>
          🚀 Enter Demo Mode
        </DemoButton>
        
        <InfoText>
          <p>✨ <strong>Demo Mode Features:</strong></p>
          <p>• Full dashboard access</p>
          <p>• Agent control interface</p>
          <p>• Performance monitoring</p>
          <p>• Settings configuration</p>
          <p>• Task management</p>
        </InfoText>
      </LoginCard>
    </LoginContainer>
  );
}

export default SimpleLogin;