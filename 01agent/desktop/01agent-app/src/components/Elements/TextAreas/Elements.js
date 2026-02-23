import styled from 'styled-components';
import breakpoint from '../../../utils/breakpoint';

export const LabeledTAContainer = styled.div`
  display: flex;

  @media screen and (${breakpoint.devices_max.xs}) {
    flex-direction: column;
  }
`

export const VerticalLabeledTAContainer = styled.div`
  display: flex;
  flex-direction: column;
`

export const TextAreaLabel = styled.div`
  font-size: ${props => props.fontSize ? props.fontSize : '16px'};
  font-weight: ${props => props.fontWeight ? props.fontWeight : '500'};
  color: var(--text-light); /* Sci-fi text color */
  padding-right: 15px;
  flex: 1 1 25%;
  margin-bottom: ${props => props.verticalLabel ? '7px' : '0px'};

  @media screen and (${breakpoint.devices_max.xs}) {
    padding-right: 0px;
    margin-bottom: 7px;
  }
`

export const TextArea = styled.textarea`
  background: var(--surface-dark); /* Sci-fi background */
  padding: ${props => props.padding ? props.padding : '10px 8px'};
  color: var(--text-light); /* Sci-fi text color */
  width: 100%;
  font-size: ${props => props.fontSize ? props.fontSize : '16px'};
  border-radius: 4px; /* Sharper corners */
  font-family: inherit;
  resize: none;
  outline: none; /* Remove default outline */
  border: 1px solid var(--border-dark); /* Sci-fi border */

  &::placeholder {
    color: rgba(var(--text-light), 0.6); /* Sci-fi placeholder color with opacity */
    font-size: ${props => props.fontSize ? props.fontSize : '16px'};
    font-weight: 300;
  }

  &:focus {
    outline: 1px solid var(--sci-fi-green); /* Sci-fi green focus outline */
  }
`

export const TextAreaError = styled.div`
  margin-top: 2px;
  color: var(--danger-color);
  font-size: 16px;
`
