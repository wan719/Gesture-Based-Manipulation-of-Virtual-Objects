function SidebarNav({ useLiveMode, connected, currentState }) {
  const items = [
    { id: "hero", label: "项目总览" },
    { id: "pipeline", label: "系统流程" },
    { id: "mode", label: "运行模式" },
    { id: "status", label: "实时状态" },
    { id: "mapping", label: "手势映射" },
    { id: "highlights", label: "项目亮点" },
    { id: "controls", label: "演示控制" },
  ];

  return (
    <aside className="panel side-nav-panel">
      <h3 className="side-title">导航</h3>
      <nav className="side-nav-list">
        {items.map((item) => (
          <a key={item.id} href={`#${item.id}`} className="side-nav-link">
            {item.label}
          </a>
        ))}
      </nav>

      <div className="side-live-box">
        <p className="side-live-label">当前模式</p>
        <p className="side-live-value">{useLiveMode ? "实时模式" : "演示模式"}</p>
        <p className="side-live-label">桥接状态</p>
        <p className={`side-live-value ${connected ? "ok" : "warn"}`}>
          {connected ? "WebSocket 已连接" : "等待连接"}
        </p>
        <p className="side-live-label">当前手势</p>
        <p className="side-live-value">{currentState.gesture}</p>
      </div>
    </aside>
  );
}

export default SidebarNav;
