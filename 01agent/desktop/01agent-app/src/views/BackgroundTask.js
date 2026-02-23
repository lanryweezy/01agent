import React from 'react';
import constants from '../utils/constants';

export default function BackgroundTask() {
  return (
    <div style={{ height: '100%', width: '100%', overflow: 'hidden', background: 'var(--background-dark)', color: 'var(--text-light)' }}>
      <iframe
        src={constants.VNC_VIEW_ONLY_URL}
        style={{ width: '100%', height: '100%', border: 'none' }}
        title="01Agent Background"
      />
    </div>
  );
}
