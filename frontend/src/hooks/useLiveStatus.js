import { useEffect, useRef, useState } from "react";

const fallbackState = {
  gesture: "OPEN_PALM",
  gestureId: 1,
  action: "idle",
  udpStatus: "连接已断开",
  timestamp: "--:--:--",
  source: "fallback",
  connectionStatus: "waiting",
  stableCount: 0,
  requiredStableFrames: 4,
};

function normalizeStatus(data, fallback = fallbackState) {
  return {
    gesture: data?.gesture ?? fallback.gesture,
    gestureId: data?.gestureId ?? data?.gesture_id ?? fallback.gestureId,
    action: data?.action ?? fallback.action,
    udpStatus: data?.udpStatus ?? data?.udp_status ?? "WebSocket 已连接",
    timestamp: data?.timestamp ?? new Date().toLocaleTimeString(),
    source: data?.source ?? "python",
    connectionStatus: "connected",
    stableCount: data?.stableCount ?? data?.stable_count ?? fallback.stableCount ?? 0,
    requiredStableFrames:
      data?.requiredStableFrames ?? data?.required_stable_frames ?? fallback.requiredStableFrames ?? 4,
  };
}

export default function useLiveStatus() {
  const [liveState, setLiveState] = useState(fallbackState);
  const [connected, setConnected] = useState(false);
  const hasConnectedRef = useRef(false);

  useEffect(() => {
    let socket;
    let shouldReconnect = true;
    let reconnectTimer;

    const markUnavailable = () => {
      const hasConnected = hasConnectedRef.current;
      setConnected(false);
      setLiveState((prev) => ({
        ...prev,
        udpStatus: hasConnected ? "连接已断开" : "等待 Python Bridge",
        source: "fallback",
        connectionStatus: hasConnected ? "disconnected" : "waiting",
      }));
    };

    const connect = () => {
      try {
        socket = new WebSocket("ws://127.0.0.1:8000/ws/status");
      } catch {
        markUnavailable();
        return;
      }

      socket.onopen = () => {
        hasConnectedRef.current = true;
        setConnected(true);
        setLiveState((prev) => ({
          ...prev,
          udpStatus: "WebSocket 已连接",
          timestamp: new Date().toLocaleTimeString(),
          source: "python",
          connectionStatus: "connected",
        }));
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLiveState((prev) => normalizeStatus(data, prev));
        } catch {
          setLiveState((prev) => ({
            ...prev,
            udpStatus: "消息解析失败",
          }));
        }
      };

      socket.onerror = () => {
        markUnavailable();
      };

      socket.onclose = () => {
        markUnavailable();
        if (shouldReconnect) {
          reconnectTimer = window.setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      shouldReconnect = false;
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      if (socket) socket.close();
    };
  }, []);

  return { liveState, connected };
}
