import { completedItems, limitationItems } from "../data/projectData";

function DefenseSummary() {
  return (
    <section className="console-panel defense-summary">
      <div>
        <p className="panel-kicker">Final System Summary</p>
        <h2>Final System Summary</h2>
      </div>

      <div className="summary-grid">
        <div>
          <h3>Completed</h3>
          <ul>
            {completedItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div>
          <h3>Limitations</h3>
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
