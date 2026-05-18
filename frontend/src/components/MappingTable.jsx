function MappingTable({ mappings }) {
  return (
    <div className="mapping-table" aria-label="Gesture mapping table">
      {mappings.map((item) => (
        <div className="mapping-row" key={item.gesture}>
          <span className="gesture-name">{item.gesture}</span>
          <span className="mapping-id">{item.id}</span>
          <span className="action-name">{item.action}</span>
        </div>
      ))}
    </div>
  );
}

export default MappingTable;
