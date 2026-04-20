import SectionTitle from "./SectionTitle";

function DemoControlPanel({ buttons, selectedAction, onSelect }) {
  return (
    <section className="panel">
      <SectionTitle
        title="演示控制"
        subtitle="前端模拟动作按钮，仅用于界面演示，当前无需连接后端。"
      />
      <div className="button-row">
        {buttons.map((item) => {
          const isActive = selectedAction.action === item.action;
          return (
            <button
              type="button"
              key={item.action}
              className={`demo-button${isActive ? " active" : ""}`}
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
