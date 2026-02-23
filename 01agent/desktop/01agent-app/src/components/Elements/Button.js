import styled from 'styled-components';

export const Button = styled.button`
  border-radius: 4px; /* Sharper corners */
  background: ${props => (props.color && !props.outlined) ? (props.color) : (props.outlined ? 'transparent' : 'var(--surface-dark)')}; /* Default to surface dark */
  padding: ${props => props.padding ? props.padding : '0px'};
  color: ${props => (props.outlined && props.color) ? props.color : (props.dark) ? 'var(--text-light)' : 'var(--text-light)'}; /* Default to text light */
  text-decoration: none;
  border: 1px solid var(--border-dark); /* Sci-fi border */
  width: ${props => props.block ? '100%' : 'auto'};
  outline: ${props => (props.outlined) ? (props.color ? (props.color + ' 2px solid') : ('var(--border-dark) 2px solid')) : 'none'}; /* Use border-dark for outline */
  box-shadow: ${props => (props.elevated ? '0 0 8px var(--sci-fi-green)' : 'none')}; /* Sci-fi glow on elevated */
  pointer-events: ${props => props.disabled ? 'none' : 'auto'};
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  font-family: inherit;
  font-size: ${props => props.fontSize ? props.fontSize : '16px'};
  font-weight: ${props => props.fontWeight ? props.fontWeight : '500'};
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  user-select: none;
  opacity: ${props => props.disabled ? '0.5' : '1.0'};

  &:hover {
    opacity: ${props => props.disabled ? '0.5' : '1.0'}; /* No opacity change on hover */
    box-shadow: 0 0 8px var(--sci-fi-green); /* Sci-fi glow on hover */
  }
`

export const BtnIcon = styled.div`
  font-size: ${props => props.iconSize ? props.iconSize : '23px'};
  height: ${props => props.iconSize ? props.iconSize : '23px'};
  color: ${props => props.color ? props.color : 'var(--sci-fi-green)'}; /* Default to sci-fi green */
  padding-right: ${props => props.left ? '10px' : '0px'};
  padding-left: ${props => props.right ? '10px' : '0px'};
  display: flex;
  align-items: center;
  justify-content: center;
`

export const IconButton = styled.div`
  font-size: ${props => props.iconSize ? props.iconSize : '23px'};
  height: ${props => props.iconSize ? props.iconSize : '23px'};
  color: ${props => props.color ? props.color : 'var(--sci-fi-green)'}; /* Default to sci-fi green */
  cursor: pointer;
  border-radius: 4px; /* Sharper corners */
  pointer-events: ${props => props.disabled ? 'none' : 'auto'};
  opacity: ${props => props.disabled ? '0.5' : '1.0'};
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: var(--surface-dark); /* Hover background */
    box-shadow: 0 0 8px var(--sci-fi-green); /* Sci-fi glow on hover */
  }
`

export const AvatarButton = styled.div`
  width: ${props => props.size ? props.size : '50px'};
  height: ${props => props.size ? props.size : '50px'};
  background: ${props => props.color ? props.color : 'var(--primary-color)'};
  box-shadow: ${props => props.raised ? '0 4pt 8pt rgb(0 0 0 / 20%)' : 'none'};
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;

  &:hover {
    opacity: ${props => props.disabled ? '0.5' : '0.8'};
  }
`

export const AvatarBtnIcon = styled.div`
  font-size: ${props => props.iconSize ? props.iconSize : '23px'};
  height: ${props => props.iconSize ? props.iconSize : '23px'};
  color: ${props => props.color ? props.color : 'var(--third-color)'};
  display: flex;
  align-items: center;
  justify-content: center;
`

export const AvatarBtnText = styled.div`
  font-size: ${props => props.fontSize ? props.fontSize : '16px'};
  padding: ${props => props.padding ? props.padding : '0px 5px'};
  font-weight: ${props => props.fontWeight ? props.fontWeight : '700'};
  color: ${props => props.color ? props.color : 'var(--third-color)'};
`
