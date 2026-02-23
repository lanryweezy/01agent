import React from 'react';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import constants from '../utils/constants';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  color: var(--text-light); /* Sci-fi text color */
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: var(--background-dark); /* Sci-fi background */
`;

const InstructionBox = styled.div`
  padding: 1rem 2rem;
  font-size: 1rem;
  line-height: 1.6;
  text-align: center;
  border-bottom: 1px solid var(--border-dark); /* Sci-fi border */
  background: var(--surface-dark); /* Sci-fi background */
`;

const Highlight = styled.span`
  font-weight: 600;
  color: var(--sci-fi-green); /* Sci-fi green highlight */
`;

const FrameWrapper = styled.div`
  flex: 1;
  iframe {
    width: 100%;
    height: 100%;
    border: none;
  }
`;

export default function BackgroundAuth() {

  const isDarkMode = useSelector(state => state.isDarkMode);

  return (
    <Container isDarkMode={isDarkMode}>
      <InstructionBox isDarkMode={isDarkMode}>
        Log in to any sites or apps you'd like <Highlight>01Agent</Highlight> to control in the background. Close the window when you finish.<br />
        <small style={{ opacity: 0.7 }}>
          These sessions are stored securely on your computer. You can always do this from App &gt; Background Mode Authentication.
        </small>
      </InstructionBox>
      <FrameWrapper>
        <iframe
          src={constants.VNC_URL}
          title="01Agent VNC Session"
        />
      </FrameWrapper>
    </Container>
  );
}
