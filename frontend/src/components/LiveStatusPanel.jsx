import { gestureMappings } from "../data/projectData";
import MappingTable from "./MappingTable";

function LiveStatusPanel({ connected, currentState, mode, onModeChange }) {
  const connectionLabel =
    mode === "demo"
      ? "Demo Mode"
      : connected
        ? "WebSocket Connected"
        : currentState.udpStatus === "Disconnected"
          ? "Disconnected"
          : "Waiting for Python Bridge";

  const statusRows = [
    ["Connection Status", connectionLabel],
    ["Current Gesture", currentState.gesture],
    ["Gesture ID", currentState.gestureId],
    ["Dog Action", currentState.action],
    ["Last Update", currentState.timestamp],
    ["Data Source", currentState.source],
    [
      "Stable Count",
      `${currentState.stableCount ?? 0} / ${currentState.requiredStableFrames ?? 4}`,
    ],
  ];

  return (
    <section className="console-panel live-status-panel panel-status-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Live Status Panel</p>
          <h2>Live Status</h2>
        </div>
        <span className={`status-dot ${connected ? "online" : "standby"}`}>
          {connected ? "Live" : "Fallback"}
        </span>
      </div>

      <div className="mode-toggle" role="group" aria-label="Runtime mode">
        <button
          type="button"
          className={mode === "live" ? "active" : ""}
          onClick={() => onModeChange("live")}
        >
          Live Mode
        </button>
        <button
          type="button"
          className={mode === "demo" ? "active" : ""}
          onClick={() => onModeChange("demo")}
        >
          Demo Mode
        </button>
      </div>

      <div className="status-list dashboard-status-grid">
        {statusRows.map(([label, value]) => (
          <div className="status-row" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <div className="bridge-hint">
        {mode === "demo"
          ? "Demo Mode is using local front-end buttons."
          : connected
            ? "WebSocket Connected. Python Bridge is streaming gesture status."
            : "Waiting for Python Bridge. The page remains available."}
      </div>

      <div className="mapping-block">
        <h3>Gesture Mapping</h3>
        <MappingTable mappings={gestureMappings} />
      </div>
    </section>
  );
}

export default LiveStatusPanel;
