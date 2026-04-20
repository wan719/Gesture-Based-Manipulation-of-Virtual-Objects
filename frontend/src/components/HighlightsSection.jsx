import SectionTitle from "./SectionTitle";
import { highlights } from "../data/projectData";

function HighlightsSection() {
  return (
    <section className="panel">
      <SectionTitle
        title="项目亮点"
        subtitle="本交互系统在工程实现层面的核心成果。"
      />
      <div className="highlights-grid">
        {highlights.map((item) => (
          <article key={item.title} className="highlight-card">
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default HighlightsSection;
