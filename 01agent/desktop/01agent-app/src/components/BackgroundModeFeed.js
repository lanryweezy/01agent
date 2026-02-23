import { useEffect, useRef } from "react";
import constants from '../utils/constants';

export default function BackgroundModeFeed() {
  const ref = useRef(null);

  useEffect(() => {
    const socket = new WebSocket(constants.BACKGROUND_MODE_WEBSOCKET_URL);
    socket.onmessage = (event) => {
      if (ref.current) {
        ref.current.src = "data:image/jpeg;base64," + event.data;
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
      // Optionally, display an error message to the user
    };

    socket.onclose = (event) => {
      console.log('WebSocket Closed:', event);
      // Optionally, inform the user that the connection was closed
    };

    return () => socket.close();
  }, []);

  return (
    <img
      ref={ref}
      style={{ width: "100%", maxWidth: 800, borderRadius: 8 }}
      alt="Live Agent View"
    />
  );
}
