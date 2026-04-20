import SectionTitle from "./SectionTitle";

function MappingTable({ mappings }) {
  const actionTextMap = {
    idle: "待机（idle）",
    forward: "前进（forward）",
    backward: "后退（backward）",
    sit: "坐下（sit）",
    wave: "挥手（wave）",
  };

  return (
    <section className="panel">
      <SectionTitle
        title="手势映射表"
        subtitle="识别到的手势类别与 Unity 动作指令的对应关系。"
      />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>手势</th>
              <th>ID</th>
              <th>动作</th>
            </tr>
          </thead>
          <tbody>
            {mappings.map((item) => (
              <tr key={item.gesture}>
                <td>{item.gesture}</td>
                <td>{item.id}</td>
                <td>{actionTextMap[item.action] ?? item.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default MappingTable;
