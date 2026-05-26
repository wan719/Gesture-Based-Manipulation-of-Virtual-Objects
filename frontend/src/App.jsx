import CameraStreamPanel from "./components/CameraStreamPanel";
import DefenseSummary from "./components/DefenseSummary";
import HeroSection from "./components/HeroSection";
import LiveStatusPanel from "./components/LiveStatusPanel";
import PipelineSection from "./components/PipelineSection";
import UnityWebGLPanel from "./components/UnityWebGLPanel";
import useLiveStatus from "./hooks/useLiveStatus";

function App() {
  const { liveState, connected } = useLiveStatus();

  const displayState = {
    ...liveState,
    source: connected ? "Python WebSocket" : "等待 Python Bridge",
    udpStatus: connected
      ? liveState.udpStatus || "WebSocket 已连接"
      : liveState.connectionStatus === "disconnected"
        ? "连接已断开"
        : "等待 Python Bridge",
  };

  return (
    <div className="app-shell">
      <div className="screen-grid" />
      <HeroSection />
      <PipelineSection />

      <main className="main-layout" aria-label="答辩展示控制台">
        <CameraStreamPanel currentState={displayState} />
        <UnityWebGLPanel currentState={displayState} />
        <LiveStatusPanel
          connected={connected}
          currentState={displayState}
        />
      </main>

      <DefenseSummary />
    </div>
  );
}

export default App;
