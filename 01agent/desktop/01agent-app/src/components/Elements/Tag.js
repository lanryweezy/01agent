import styled from 'styled-components';

export const Tag = styled.div`
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 500;
  background-color: var(--surface-dark); /* Use dark surface for background */
  color: var(--sci-fi-green); /* Sci-fi green text */
  border: 1px solid var(--sci-fi-green); /* Sci-fi green border */
  border-radius: 4px; /* Sharper corners */
  gap: 6px;
  user-select: none;
`;
