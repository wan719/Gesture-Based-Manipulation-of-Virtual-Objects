import SectionTitle from "./SectionTitle";

function StatusCards({ currentState }) {
  const cards = [
    { label: "当前手势", value: currentState.gesture },
    { label: "手势 ID", value: currentState.gestureId },
    { label: "机械狗动作", value: currentState.action?.toUpperCase?.() ?? "NONE" },
    { label: "UDP 状态", value: currentState.udpStatus },
    { label: "最后更新时间", value: currentState.timestamp ?? "--:--:--" },
    { label: "数据来源", value: currentState.source ?? "unknown" },
  ];

  return (
    <section className="panel">
      <SectionTitle
        title="实时状态控制台"
        subtitle="用于答辩展示与调试的手势识别和机械狗控制实时状态面板。"
      />
      <div className="status-grid status-grid-6">
        {cards.map((item) => (
          <article key={item.label} className="status-card">
            <p className="status-label">{item.label}</p>
            <p className="status-value">{item.value}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default StatusCards;
