import { actionButtons, gestureMappings } from "../data/projectData";
import MappingTable from "./MappingTable";

function formatDataSource(source) {
  const sourceMap = {
    fallback: "备用数据",
    python: "Python 实时识别",
    "Python WebSocket": "Python WebSocket",
    "等待 Python Bridge": "等待 Python Bridge",
    "前端演示": "前端演示",
  };

  return sourceMap[source] ?? source ?? "未知";
}

function LiveStatusPanel({ connected, currentState }) {
  const actionLabel =
    actionButtons.find((item) => item.action === currentState.action)?.label ?? currentState.action;
  const connectionLabel =
    connected
      ? "WebSocket 已连接"
      : currentState.connectionStatus === "disconnected"
        ? "连接已断开"
        : "等待 Python Bridge";

  const statusRows = [
    ["连接状态", connectionLabel],
    ["当前手势", currentState.gesture],
    ["手势 ID", currentState.gestureId],
    ["机械狗动作", actionLabel],
    ["最后更新", currentState.timestamp],
    ["数据来源", formatDataSource(currentState.source)],
    [
      "稳定帧数",
      `${currentState.stableCount ?? 0} / ${currentState.requiredStableFrames ?? 4}`,
    ],
  ];

  return (
    <section className="console-panel live-status-panel panel-status-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">实时状态面板</p>
          <h2>实时状态</h2>
        </div>
        <span className={`status-dot ${connected ? "online" : "standby"}`}>
          {connected ? "实时" : "备用"}
        </span>
      </div>

      <div className="live-mode-badge" aria-label="当前运行模式">
        <span>运行模式</span>
        <strong>实时模式</strong>
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
        {connected
          ? "WebSocket 已连接，Python Bridge 正在推送手势状态。"
          : "等待 Python Bridge，请先启动 Python 实时识别服务。"}
      </div>

      <div className="mapping-block">
        <h3>手势映射</h3>
        <MappingTable mappings={gestureMappings} />
      </div>
    </section>
  );
}

export default LiveStatusPanel;
