import { techTags } from "../data/projectData";

function HeroSection() {
  return (
    <header className="hero-section">
      <div className="hero-copy">
        <p className="eyebrow">答辩展示控制台</p>
        <h1>基于手势识别的虚拟机械狗交互控制系统</h1>
        <p className="hero-subtitle">Gesture-Based Manipulation of Virtual Objects</p>
      </div>

      <div className="tag-row" aria-label="技术标签">
        {techTags.map((tag) => (
          <span className="tech-tag" key={tag}>
            {tag}
          </span>
        ))}
      </div>
    </header>
  );
}

export default HeroSection;
