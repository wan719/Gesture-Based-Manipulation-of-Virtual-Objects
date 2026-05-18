function DemoControlPanel({ buttons, mode, selectedAction, onSelect }) {
  return (
    <section className="console-panel demo-control-panel">
      <div>
        <p className="panel-kicker">Demo Control</p>
        <h2>Front-end Action Simulator</h2>
        <p className="panel-note">
          Demo Mode 下可直接模拟 Unity 动作状态；Live Mode 下页面优先等待 Python Bridge 数据。
        </p>
      </div>

      <div className="demo-actions">
        {buttons.map((item) => {
          const isActive = selectedAction.action === item.action && mode === "demo";
          return (
            <button
              type="button"
              key={item.action}
              className={`action-button${isActive ? " active" : ""}`}
              onClick={() => onSelect(item)}
            >
              {item.label}
            </button>
          );
        })}
      </div>
    </section>
  );
}

export default DemoControlPanel;
