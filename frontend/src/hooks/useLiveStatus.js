import { useEffect, useState } from "react";

const defaultState = {
  gesture: "OPEN_PALM",
  gestureId: 1,
  action: "idle",
  udpStatus: "Connecting...",
  timestamp: "--:--:--",
  source: "demo",
};

export default function useLiveStatus() {
  const [liveState, setLiveState] = useState(defaultState);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/status");

    ws.onopen = () => {
      setConnected(true);
      setLiveState((prev) => ({
        ...prev,
        udpStatus: "Connected",
      }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLiveState({
          gesture: data.gesture ?? "UNKNOWN",
          gestureId: data.gestureId ?? 5,
          action: data.action ?? "none",
          udpStatus: "Connected",
          timestamp: data.timestamp ?? "--:--:--",
          source: data.source ?? "python",
        });
      } catch (error) {
        console.error("WebSocket parse error:", error);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setLiveState((prev) => ({
        ...prev,
        udpStatus: "Disconnected",
      }));
    };

    ws.onerror = () => {
      setConnected(false);
      setLiveState((prev) => ({
        ...prev,
        udpStatus: "Disconnected",
      }));
    };

    return () => ws.close();
  }, []);

  return { liveState, connected };
}
