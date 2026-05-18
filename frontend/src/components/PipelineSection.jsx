import { pipelineSteps } from "../data/projectData";

function PipelineSection() {
  return (
    <section className="pipeline-section" aria-label="System pipeline">
      {pipelineSteps.map((step, index) => (
        <div className="pipeline-node" key={step}>
          <span className="pipeline-index">{String(index + 1).padStart(2, "0")}</span>
          <span>{step}</span>
        </div>
      ))}
    </section>
  );
}

export default PipelineSection;
