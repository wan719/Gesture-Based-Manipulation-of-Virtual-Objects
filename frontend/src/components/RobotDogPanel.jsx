import { useState } from "react";
import { actionButtons, actionDescriptions } from "../data/projectData";

function RobotDogPlaceholder() {
  return (
    <div className="unity-placeholder">
      <div className="unity-grid-floor" />
      <div className="robot-core">
        <span className="robot-head" />
        <span className="robot-body" />
        <span className="robot-leg leg-a" />
        <span className="robot-leg leg-b" />
        <span className="robot-leg leg-c" />
        <span className="robot-leg leg-d" />
      </div>
      <div className="unity-overlay">
        <strong>Unity Scene Preview</strong>
        <span>Robot dog runtime window placeholder</span>
      </div>
    </div>
  );
}

function RobotDogPanel({ currentState }) {
  const [mediaMode, setMediaMode] = useState("video");
  const action = currentState.action || "idle";
  const actionText = action.toUpperCase();
  const description =
    actionDescriptions[action] ?? "Robot dog is waiting for gesture command.";

  return (
    <section className="console-panel robot-panel panel-robot-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Virtual Robot Dog Panel</p>
          <h2>Virtual Robot Dog</h2>
        </div>
        <span className="status-dot online">Unity Preview</span>
      </div>

      <div className="robot-preview">
        <div className="robot-hud-label hud-top-left">UNITY VIEWPORT</div>
        <div className="robot-hud-label hud-top-right">{actionText}</div>
        {mediaMode === "video" && (
          <video
            className="robot-media"
            src="/robotdog-demo.mp4"
            autoPlay
            muted
            loop
            playsInline
            onError={() => setMediaMode("image")}
          />
        )}

        {mediaMode === "image" && (
          <img
            className="robot-media"
            src="/robotdog-preview.png"
            alt="Unity robot dog preview"
            onError={() => setMediaMode("placeholder")}
          />
        )}

        {mediaMode === "placeholder" && <RobotDogPlaceholder />}
      </div>

      <div className="robot-action-readout">
        <span>Action</span>
        <strong>{actionText}</strong>
        <p>{description}</p>
      </div>

      <div className="action-capsules" aria-label="Robot dog action tags">
        {actionButtons.map((item) => (
          <span
            className={`action-capsule${item.action === action ? " active" : ""}`}
            key={item.action}
          >
            {item.label}
          </span>
        ))}
      </div>
    </section>
  );
}

export default RobotDogPanel;
