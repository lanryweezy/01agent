import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import styled from 'styled-components';

const Wrapper = styled.div`
  padding: 30px;
  color: var(--text-light); /* Sci-fi text color */
  text-align: center;
  background: var(--background-dark); /* Sci-fi background */
  height: 100vh; /* Full height */
  width: 100vw; /* Full width */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const ProgressBar = styled.div`
  height: 10px;
  width: 100%;
  background: var(--surface-dark); /* Sci-fi background */
  border-radius: 4px; /* Sharper corners */
  margin-top: 20px;
  border: 1px solid var(--border-dark); /* Sci-fi border */
`;

const Fill = styled.div`
  height: 100%;
  width: ${props => props.pct}%;
  background: var(--sci-fi-green); /* Sci-fi green fill */
  border-radius: 4px; /* Sharper corners */
  transition: width 0.3s ease;
`;

export default function BackgroundSetup() {
  const [status, setStatus] = useState('Working...');
  const [progress, setProgress] = useState(0);

  const isDarkMode = useSelector(state => state.isDarkMode);

  useEffect(() => {
    window.electronAPI.onSetupStatus(setStatus);
    window.electronAPI.onSetupProgress(setProgress);
    window.electronAPI.onSetupComplete(result => {
      if (result.success) {
        setStatus('Setup Complete! You can now use Background Mode.');
        setTimeout(() => window.close(), 4000);
      } else {
        setStatus(`${result.error || 'Setup Failed: Please ensure you have Windows 10 or higher and that virtualization is enabled in BIOS.'}`);
      }
    });
    window.electronAPI.startBackgroundSetup();
  }, []);

  return (
    <Wrapper isDarkMode={isDarkMode}>
      <div style={{fontSize: '18px', fontWeight: '600'}}>Setting up Background Mode</div>
      <p style={{fontSize: '16px', fontWeight: '400'}}>{status}</p>
      <ProgressBar>
        <Fill pct={progress} />
      </ProgressBar>
    </Wrapper>
  );
}
