import { useMemo, useState } from "react";
import DemoControlPanel from "./components/DemoControlPanel";
import Footer from "./components/Footer";
import HeroSection from "./components/HeroSection";
import HighlightsSection from "./components/HighlightsSection";
import MappingTable from "./components/MappingTable";
import PipelineSection from "./components/PipelineSection";
import SidebarNav from "./components/SidebarNav";
import StatusCards from "./components/StatusCards";
import { actionButtons, gestureMappings } from "./data/projectData";
import useLiveStatus from "./hooks/useLiveStatus";

function App() {
  const [selectedAction, setSelectedAction] = useState(actionButtons[0]);
  const [useLiveMode, setUseLiveMode] = useState(true);

  const { liveState, connected } = useLiveStatus();

  const demoState = useMemo(() => {
    const matched = gestureMappings.find(
      (item) => item.action === selectedAction.action
    );

    return {
      gesture: matched ? matched.gesture : "OPEN_PALM",
      gestureId: matched ? matched.id : 1,
      action: selectedAction.action,
      udpStatus: "Demo Mode",
      timestamp: "--:--:--",
      source: "demo",
    };
  }, [selectedAction]);

  const currentState = useLiveMode ? liveState : demoState;

  return (
    <div className="app-shell">
      <div className="background-glow bg-glow-top" />
      <div className="background-glow bg-glow-bottom" />

      <div className="main-layout">
        <SidebarNav
          useLiveMode={useLiveMode}
          connected={connected}
          currentState={currentState}
        />

        <main className="content-layout">
          <section id="hero">
            <HeroSection />
          </section>

          <section id="pipeline">
            <PipelineSection />
          </section>

          <section id="mode" className="panel">
            <div className="section-head">
              <h2>系统模式</h2>
              <p>可在实时 Python 数据和本地前端演示模式之间切换。</p>
            </div>

            <div className="button-row mode-switch-row">
              <button
                className={`demo-button${useLiveMode ? " active" : ""}`}
                onClick={() => setUseLiveMode(true)}
                type="button"
              >
                实时模式（Live Mode）
              </button>
              <button
                className={`demo-button${!useLiveMode ? " active" : ""}`}
                onClick={() => setUseLiveMode(false)}
                type="button"
              >
                演示模式（Demo Mode）
              </button>
            </div>

            <div className="mode-status">
              <strong>连接状态：</strong>
              {connected ? "WebSocket 已连接" : "等待 Python Bridge 服务"}
            </div>
            <div className="mode-status">
              <strong>实时事件：</strong>
              {`${currentState.gesture} -> ${currentState.action}`}
            </div>
          </section>

          <section id="status">
            <StatusCards currentState={currentState} />
          </section>

          <section id="mapping">
            <MappingTable mappings={gestureMappings} />
          </section>

          <section id="highlights">
            <HighlightsSection />
          </section>

          <section id="controls">
            {!useLiveMode ? (
              <DemoControlPanel
                buttons={actionButtons}
                selectedAction={selectedAction}
                onSelect={setSelectedAction}
              />
            ) : (
              <section className="panel">
                <div className="section-head">
                  <h2>演示控制</h2>
                  <p>当前为实时模式，按钮演示区已隐藏。切换到 Demo Mode 可手动触发动作展示。</p>
                </div>
              </section>
            )}
          </section>
        </main>
      </div>

      <Footer />
    </div>
  );
}

export default App;
