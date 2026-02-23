import styled from 'styled-components';
import breakpoint from '../../utils/breakpoint';

export const AppTheme = styled.div`
  background: ${props => props.isDarkMode ? 'var(--background-dark)' : 'var(--light-background)'};
  color-scheme: ${props => props.isDarkMode ? 'dark' : 'light'};
  min-height: 100vh;
`

export const AppMainContainer = styled.div`
  display: flex;
  height: 100vh;
  color: var(--text-light); /* Changed from white to use theme variable */
`;

export const OverlayContainer = styled.div`
  background: ${props => props.isDarkMode ? 'var(--background-dark)' : 'var(--light-background)'}; /* Changed to use background-dark for consistency */
  color-scheme: ${props => props.isDarkMode ? 'dark' : 'light'};
  height: 100vh;
  width: 100vw;
  overflow: hidden;
`

export const Row = styled.div`
  display: flex;
  flex-wrap: wrap;
  -webkit-box-flex: 1;
  flex: 1 1 auto;
  width: 100%;
  justify-content: ${props => props.justifyContent ? props.justifyContent : 'flex-start'};
  align-items: ${props => props.alignItems ? props.alignItems : 'stretch'};
`

export const Column = styled.div`
  color: ${props => props.isDarkMode ? 'var(--light-background)' : 'var(--third-color)'};
  -webkit-box-flex: 0;
  padding: 10px;
  flex: 0 0 ${props => breakpoint.checkers.getFlexWidth(props.cols ? props.cols : 12)};
  max-width: ${props => breakpoint.checkers.getFlexWidth(props.cols ? props.cols : 12)};

  @media screen and (${breakpoint.devices_max.lg}) {
    flex: 0 0 ${props => breakpoint.checkers.getFlexWidth(props.lg ? props.lg : props.cols)};
    max-width: ${props => breakpoint.checkers.getFlexWidth(props.lg ? props.lg : props.cols)};
  }

  @media screen and (${breakpoint.devices_max.md}) {
    flex: 0 0 ${props => breakpoint.checkers.getFlexWidth(props.md ? props.md : props.cols)};
    max-width: ${props => breakpoint.checkers.getFlexWidth(props.md ? props.md : props.cols)};
  }

  @media screen and (${breakpoint.devices_max.sm}) {
    flex: 0 0 ${props => breakpoint.checkers.getFlexWidth(props.sm ? props.sm : props.cols)};
    max-width: ${props => breakpoint.checkers.getFlexWidth(props.sm ? props.sm : props.cols)};
  }

  @media screen and (${breakpoint.devices_max.xs}) {
    flex: 0 0 ${props => breakpoint.checkers.getFlexWidth(props.xs ? props.xs : props.cols)};
    max-width: ${props => breakpoint.checkers.getFlexWidth(props.xs ? props.xs : props.cols)};
  }
`