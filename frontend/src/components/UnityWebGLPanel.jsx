import { useEffect, useRef } from "react";
import { actionButtons, actionDescriptions } from "../data/projectData";
import useUnityWebGL, {
  UNITY_BUILD_CONFIG,
  UNITY_CANVAS_ID,
  UNITY_TARGET_METHOD,
  UNITY_TARGET_OBJECT,
} from "../hooks/useUnityWebGL";

function UnityBuildPlaceholder({ status, progress, error }) {
  const isLoading = status === "loading";
  const title = isLoading
    ? `Loading Unity WebGL... ${progress}%`
    : "Unity WebGL Load Error";
  const message =
    error || "Check loader.js, data, framework.js, wasm, and browser console.";

  return (
    <div className="unity-placeholder unity-webgl-placeholder">
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
        <strong>{title}</strong>
        <span className="unity-error-message">{message}</span>
      </div>
    </div>
  );
}

function UnityWebGLPanel({ currentState }) {
  const canvasRef = useRef(null);
  const { status, progress, error, bannerMessage, sendAction } = useUnityWebGL(canvasRef);
  const action = currentState.action || "idle";
  const actionText = action.toUpperCase();
  const description =
    actionDescriptions[action] ?? "Robot dog is waiting for a stable gesture command.";

  useEffect(() => {
    if (status === "ready") {
      sendAction(action);
    }
  }, [action, sendAction, status]);

  return (
    <section className="console-panel robot-panel panel-robot-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Unity WebGL Panel</p>
          <h2>Unity WebGL Virtual Robot Dog</h2>
        </div>
        <span className={`status-dot ${status === "ready" ? "online" : "standby"}`}>
          {status === "ready" ? "Unity Ready" : status === "loading" ? `Loading ${progress}%` : "Load Error"}
        </span>
      </div>

      <div className="robot-preview unity-webgl-preview">
        <div className="robot-hud-label hud-top-left">UNITY WEBGL</div>
        <div className="robot-hud-label hud-top-right">{actionText}</div>
        <canvas
          id={UNITY_CANVAS_ID}
          ref={canvasRef}
          className={`unity-canvas ${status === "ready" ? "active" : ""}`}
          tabIndex={0}
        />
        {status !== "ready" && (
          <UnityBuildPlaceholder status={status} progress={progress} error={error} />
        )}
      </div>

      <div className="robot-action-readout">
        <span>Action</span>
        <strong>{actionText}</strong>
        <p>{description}</p>
      </div>

      <div className="unity-path-note">
        Target: {UNITY_TARGET_OBJECT}.{UNITY_TARGET_METHOD}(action) | Loader: {UNITY_BUILD_CONFIG.loaderUrl}
        {bannerMessage ? ` | Unity: ${bannerMessage}` : ""}
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

export default UnityWebGLPanel;
