import { useEffect, useRef } from "react";
import { actionButtons, actionDescriptions } from "../data/projectData";
import useUnityWebGL, {
  UNITY_BUILD_CONFIG,
  UNITY_CANVAS_ID,
  UNITY_TARGET_METHOD,
  UNITY_TARGET_OBJECT,
  UNITY_TARGET_TURN_METHOD,
} from "../hooks/useUnityWebGL";

function UnityBuildPlaceholder({ status, progress, error }) {
  const isLoading = status === "loading";
  const title = isLoading
    ? `正在加载 Unity WebGL... ${progress}%`
    : "Unity WebGL 加载失败";
  const message =
    error || "请检查 loader.js、data、framework.js、wasm 文件和浏览器控制台。";

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
  const { status, progress, error, bannerMessage, sendAction, sendTurn } = useUnityWebGL(canvasRef);
  const action = currentState.action || "idle";
  const actionLabel = actionButtons.find((item) => item.action === action)?.label ?? action.toUpperCase();
  const description =
    actionDescriptions[action] ?? "等待稳定手势指令。";

  useEffect(() => {
    if (status === "ready") {
      sendAction(action);
      sendTurn(window.__gestureDashboardTurnCommand || "stop");
    }
  }, [action, currentState.commandSerial, sendAction, sendTurn, status]);

  useEffect(() => {
    const handleTurnCommand = (event) => {
      if (status === "ready") {
        sendTurn(event.detail || "stop");
      }
    };

    window.addEventListener("gesture-dashboard-turn", handleTurnCommand);
    return () => window.removeEventListener("gesture-dashboard-turn", handleTurnCommand);
  }, [sendTurn, status]);

  return (
    <section className="console-panel robot-panel panel-robot-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Unity WebGL 面板</p>
          <h2>Unity WebGL 虚拟机械狗</h2>
        </div>
        <span className={`status-dot ${status === "ready" ? "online" : "standby"}`}>
          {status === "ready" ? "Unity 就绪" : status === "loading" ? `加载中 ${progress}%` : "加载失败"}
        </span>
      </div>

      <div className="robot-preview unity-webgl-preview">
        <div className="robot-hud-label hud-top-left">UNITY WEBGL</div>
        <div className="robot-hud-label hud-top-right">{actionLabel}</div>
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
        <span>当前动作</span>
        <strong>{actionLabel}</strong>
        <p>{description}</p>
      </div>

      <div className="unity-path-note">
        Unity 调用目标：{UNITY_TARGET_OBJECT}.{UNITY_TARGET_METHOD}(动作) / {UNITY_TARGET_TURN_METHOD}(转向) | 加载器：{UNITY_BUILD_CONFIG.loaderUrl}
        {bannerMessage ? ` | Unity: ${bannerMessage}` : ""}
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

export default UnityWebGLPanel;
