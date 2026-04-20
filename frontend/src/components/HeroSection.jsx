import { techTags } from "../data/projectData";

function HeroSection() {
  return (
    <section className="panel hero-panel">
      <div className="hero-content">
        <p className="eyebrow">项目展示控制台</p>
        <h1>Gesture-Based Manipulation of Virtual Objects</h1>
        <p className="hero-description">
          一个基于手势识别的人机交互演示系统，通过 Python 到 Unity 的链路实时控制虚拟机械狗。
        </p>
        <div className="tag-row">
          {techTags.map((tag) => (
            <span key={tag} className="tech-tag">
              {tag}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HeroSection;
