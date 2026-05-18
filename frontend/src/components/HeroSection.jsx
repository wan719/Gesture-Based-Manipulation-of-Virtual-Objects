import { techTags } from "../data/projectData";

function HeroSection() {
  return (
    <header className="hero-section">
      <div className="hero-copy">
        <p className="eyebrow">Defense Console</p>
        <h1>Gesture-Based Manipulation of Virtual Objects</h1>
        <p className="hero-subtitle">基于手势识别的虚拟机械狗交互控制系统</p>
      </div>

      <div className="tag-row" aria-label="Technology tags">
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
