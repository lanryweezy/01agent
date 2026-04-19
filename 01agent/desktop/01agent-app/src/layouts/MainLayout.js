import React from 'react';
import styled from 'styled-components';
import ModernSidebar from './ModernSidebar';
import theme from '../theme/GlobalTheme';
import { useSelector } from 'react-redux';

const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: ${props => props.isDarkMode ? theme.colors.dark.background : theme.colors.light.background};
`;

const ContentArea = styled.main`
  flex: 1;
  height: 100%;
  overflow-y: auto;
  position: relative;
`;

const MainLayout = ({ children }) => {
  const isDarkMode = useSelector(state => state.isDarkMode);

  return (
    <LayoutContainer isDarkMode={isDarkMode}>
      <ModernSidebar />
      <ContentArea>
        {children}
      </ContentArea>
    </LayoutContainer>
  );
};

export default MainLayout;
