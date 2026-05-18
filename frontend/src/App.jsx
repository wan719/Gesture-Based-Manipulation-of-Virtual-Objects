import { useMemo, useState } from "react";
import CameraStreamPanel from "./components/CameraStreamPanel";
import DefenseSummary from "./components/DefenseSummary";
import DemoControlPanel from "./components/DemoControlPanel";
import HeroSection from "./components/HeroSection";
import LiveStatusPanel from "./components/LiveStatusPanel";
import PipelineSection from "./components/PipelineSection";
import UnityWebGLPanel from "./components/UnityWebGLPanel";
import { actionButtons, gestureMappings } from "./data/projectData";
import useLiveStatus from "./hooks/useLiveStatus";

const initialAction = actionButtons.find((item) => item.action === "idle") ?? actionButtons[0];

function buildStateFromAction(actionItem) {
  const matched = gestureMappings.find((item) => item.action === actionItem.action);

  return {
    gesture: matched?.gesture ?? "OPEN_PALM",
    gestureId: matched?.id ?? 1,
    action: matched?.action ?? actionItem.action,
    udpStatus: "Demo Ready",
    timestamp: new Date().toLocaleTimeString(),
    source: "demo",
    stableCount: 4,
    requiredStableFrames: 4,
  };
}

function App() {
  const [mode, setMode] = useState("live");
  const [selectedAction, setSelectedAction] = useState(initialAction);
  const { liveState, connected } = useLiveStatus();

  const demoState = useMemo(() => buildStateFromAction(selectedAction), [selectedAction]);
  const isLiveMode = mode === "live";
  const currentState = isLiveMode ? liveState : demoState;
  const dataSource = isLiveMode
    ? connected
      ? "Python WebSocket"
      : "Waiting for Bridge"
    : "Frontend Demo";

  const displayState = {
    ...currentState,
    source: dataSource,
    udpStatus: isLiveMode
      ? connected
        ? currentState.udpStatus || "WebSocket Connected"
        : currentState.connectionStatus === "disconnected"
          ? "Disconnected"
          : "Waiting for Python Bridge"
      : "Demo Ready",
  };

  const handleDemoSelect = (actionItem) => {
    setSelectedAction(actionItem);
    setMode("demo");
  };

  return (
    <div className="app-shell">
      <div className="screen-grid" />
      <HeroSection />
      <PipelineSection />

      <main className="main-layout" aria-label="Defense dashboard console">
        <CameraStreamPanel currentState={displayState} mode={mode} />
        <UnityWebGLPanel currentState={displayState} />
        <LiveStatusPanel
          connected={connected}
          currentState={displayState}
          mode={mode}
          onModeChange={setMode}
        />
      </main>

      <DemoControlPanel
        buttons={actionButtons}
        mode={mode}
        selectedAction={selectedAction}
        onSelect={handleDemoSelect}
      />

      <DefenseSummary />
    </div>
  );
}

export default App;
