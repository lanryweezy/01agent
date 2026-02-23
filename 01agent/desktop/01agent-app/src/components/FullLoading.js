import React from 'react';
import ClipLoader from "react-spinners/ClipLoader";
import styled from 'styled-components';

const FullLoadingContainer = styled.div`
  height: 100%;
  z-index: 2000;
  position: fixed;
  width: 100%;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
`;

function FullLoading() {
  return (
    <FullLoadingContainer>
        <ClipLoader
          color="var(--light-background)"
          size={150}
        />
    </FullLoadingContainer>
  );
}

export default FullLoading;