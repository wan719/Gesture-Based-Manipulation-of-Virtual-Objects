import { actionButtons } from "../data/projectData";

function MappingTable({ mappings }) {
  return (
    <div className="mapping-table" aria-label="手势映射表">
      {mappings.map((item) => {
        const actionLabel = actionButtons.find((button) => button.action === item.action)?.label ?? item.action;
        return (
          <div className="mapping-row" key={item.gesture}>
            <span className="gesture-name">{item.gesture}</span>
            <span className="mapping-id">{item.id}</span>
            <span className="action-name">{actionLabel}</span>
          </div>
        );
      })}
    </div>
  );
}

export default MappingTable;
