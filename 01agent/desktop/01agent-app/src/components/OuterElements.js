import styled from 'styled-components';

export const MainContainer = styled.div`
  width: 100%;
  background: var(--background-dark); /* Sci-fi background */
`

export const AccountContainer = styled.div`
  min-height: 100vh;
  padding: 15px;
  max-width: var(--max-login-width);
  margin-left: auto;
  margin-right: auto;
`

export const AccountHeader = styled.div`
  display: flex;
  align-items: center;
  margin-top: 20px;
`

export const AccountDiv = styled.div`
  min-height: 80vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`

export const InfoContainer = styled.div`
  width: 100%;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  color: var(--text-light); /* Sci-fi text color */
  display: flex;
  flex-direction: column;
`

export const FormTitle = styled.div`
  font-size: 40px;
  text-align: center;
  font-weight: 300;
  color: var(--text-light); /* Sci-fi text color */
`

export const AccountTextField = styled.input`
  background: var(--surface-dark); /* Sci-fi background */
  width: 100%;
  padding: 16px 20px;
  color: var(--text-light); /* Sci-fi text color */
  font-size: 18px;
  margin-bottom: 20px;
  border-radius: 4px; /* Sharper corners */
  font-family: inherit;
  transition: 0.1s ease;
  resize: none;
  outline: none;
  border: 1px solid var(--border-dark); /* Sci-fi border */

  &::placeholder {
    color: rgba(var(--text-light), 0.6); /* Sci-fi placeholder color with opacity */
    font-size: 18px;
    font-weight: 500;
    user-select: none;
  }

  &:focus {
    outline: 1px solid var(--sci-fi-green); /* Sci-fi green focus outline */
  }
`

export const OrDiv = styled.div`
  display: flex;
  align-items: center;
  text-align: center;

  &::before, &::after {
  content: '';
  flex: 1;
  border-bottom: 2px solid var(--border-dark); /* Sci-fi border color */
  margin: 0 10px;
}
`
