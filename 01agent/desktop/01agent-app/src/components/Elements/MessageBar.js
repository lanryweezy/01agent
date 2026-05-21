import React from 'react';
import styled from 'styled-components';

const MessageBarContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
`;

const MessageItem = styled.div`
  background: ${props => props.type === 'error' ? '#ff4757' : props.type === 'success' ? '#2ed573' : '#3742fa'};
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  animation: slideIn 0.3s ease-out;
  
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;

// ⚡ Bolt: Wrapped MessageBar in React.memo to prevent unnecessary re-renders
// when parent components update high-frequency state, since the messages array
// only changes on specific events.
const MessageBar = React.memo(({ messages = [] }) => {
  if (!messages || messages.length === 0) return null;

  return (
    <MessageBarContainer>
      {messages.map((message, index) => (
        <MessageItem key={index} type={message.type}>
          {message.text}
        </MessageItem>
      ))}
    </MessageBarContainer>
  );
});

export default MessageBar;