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
        <strong>Unity 场景预览</strong>
        <span>机械狗运行窗口占位展示</span>
      </div>
    </div>
  );
}

function RobotDogPanel({ currentState }) {
  const [mediaMode, setMediaMode] = useState("video");
  const action = currentState.action || "idle";
  const actionText = actionButtons.find((item) => item.action === action)?.label ?? action;
  const description =
    actionDescriptions[action] ?? "机械狗正在等待稳定手势指令。";

  return (
    <section className="console-panel robot-panel panel-robot-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">虚拟机械狗面板</p>
          <h2>虚拟机械狗</h2>
        </div>
        <span className="status-dot online">Unity 预览</span>
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
            alt="Unity 机械狗预览"
            onError={() => setMediaMode("placeholder")}
          />
        )}

        {mediaMode === "placeholder" && <RobotDogPlaceholder />}
      </div>

      <div className="robot-action-readout">
        <span>当前动作</span>
        <strong>{actionText}</strong>
        <p>{description}</p>
      </div>

      <div className="action-capsules" aria-label="机械狗动作标签">
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
