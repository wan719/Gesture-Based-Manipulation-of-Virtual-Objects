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
    let ws;
    let pollTimer;
    let wsConnected = false;

    const updateByHttp = async () => {
      if (wsConnected) return;
      try {
        const resp = await fetch("http://127.0.0.1:8000/api/status");
        if (!resp.ok) return;
        const data = await resp.json();
        setLiveState((prev) => ({
          ...prev,
          gesture: data.gesture ?? prev.gesture,
          gestureId: data.gestureId ?? prev.gestureId,
          action: data.action ?? prev.action,
          udpStatus: "Bridge Online",
          timestamp: data.timestamp ?? prev.timestamp,
          source: data.source ?? prev.source,
        }));
      } catch {
        // ignore
      }
    };

    try {
      ws = new WebSocket("ws://127.0.0.1:8000/ws/status");

      ws.onopen = () => {
        wsConnected = true;
        setConnected(true);
        setLiveState((prev) => ({ ...prev, udpStatus: "Connected" }));
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
        wsConnected = false;
        setConnected(false);
        setLiveState((prev) => ({ ...prev, udpStatus: "Disconnected" }));
      };

      ws.onerror = () => {
        wsConnected = false;
        setConnected(false);
        setLiveState((prev) => ({ ...prev, udpStatus: "Disconnected" }));
      };
    } catch {
      setConnected(false);
    }

    pollTimer = window.setInterval(updateByHttp, 5000);
    updateByHttp();

    return () => {
      if (ws) ws.close();
      if (pollTimer) window.clearInterval(pollTimer);
    };
  }, []);

  return { liveState, connected };
}
