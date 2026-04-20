import SectionTitle from "./SectionTitle";
import { pipelineSteps } from "../data/projectData";

function PipelineSection() {
  return (
    <section className="panel">
      <SectionTitle
        title="系统流程"
        subtitle="从摄像头手势输入到虚拟机械狗动作输出的端到端数据链路。"
      />
      <div className="pipeline-track">
        {pipelineSteps.map((step, index) => (
          <div key={step} className="pipeline-item">
            <span className="pipeline-index">{String(index + 1).padStart(2, "0")}</span>
            <p>{step}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default PipelineSection;
