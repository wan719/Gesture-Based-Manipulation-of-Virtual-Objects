import { completedItems, limitationItems } from "../data/projectData";

function DefenseSummary() {
  return (
    <section className="console-panel defense-summary">
      <div>
        <p className="panel-kicker">最终系统总结</p>
        <h2>最终系统总结</h2>
      </div>

      <div className="summary-grid">
        <div>
          <h3>已完成</h3>
          <ul>
            {completedItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3>当前不足</h3>
          <ul>
            {limitationItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default DefenseSummary;
