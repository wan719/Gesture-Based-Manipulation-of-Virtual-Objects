export const techTags = [
  "MediaPipe",
  "Python",
  "FastAPI",
  "WebSocket",
  "Unity WebGL",
  "React 控制台",
];

export const pipelineSteps = [
  "摄像头",
  "Python MediaPipe 服务",
  "WebSocket / MJPEG",
  "React 控制台",
  "Unity WebGL",
  "机械狗",
];

export const gestureMappings = [
  {
    gesture: "FIST",
    id: 0,
    action: "sit",
    description: "机械狗执行下蹲动作。",
  },
  {
    gesture: "OPEN_PALM",
    id: 1,
    action: "idle",
    description: "机械狗保持待机状态。",
  },
  {
    gesture: "POINT_INDEX",
    id: 2,
    action: "forward",
    description: "机械狗向前移动。",
  },
  {
    gesture: "VICTORY",
    id: 3,
    action: "backward",
    description: "机械狗向后移动。",
  },
  {
    gesture: "THUMBS_UP",
    id: 4,
    action: "wave",
    description: "机械狗执行挥手互动。",
  },
  {
    gesture: "ROCK",
    id: 6,
    action: "jump",
    description: "机械狗执行跳跃动作。",
  },
  {
    gesture: "THREE",
    id: 7,
    action: "stand",
    description: "机械狗进入站立展示姿态。",
  },
];

export const actionButtons = [
  { label: "待机", action: "idle" },
  { label: "前进", action: "forward" },
  { label: "后退", action: "backward" },
  { label: "下蹲", action: "sit" },
  { label: "挥手", action: "wave" },
  { label: "跳跃", action: "jump" },
  { label: "站立", action: "stand" },
];

export const actionDescriptions = {
  idle: "机械狗保持待机状态。",
  forward: "机械狗正在向前移动。",
  backward: "机械狗正在向后移动。",
  sit: "机械狗执行下蹲动作。",
  wave: "机械狗执行挥手互动。",
  jump: "机械狗执行跳跃动作。",
  stand: "机械狗保持站立展示姿态。",
  none: "等待稳定手势指令。",
};

export const completedItems = [
  "MediaPipe 手势识别",
  "稳定帧手势分类",
  "Python 与 Unity 通信联调",
  "Unity 机械狗动作控制",
  "Web 展示控制台",
  "Python 实时识别画面流",
  "Unity WebGL 接入设计",
];

export const limitationItems = [
  "Unity WebGL 仍需要在 Unity Editor 中手动导出",
  "机械狗动画仍属于基础代码驱动动画",
  "Unity 场景背景仍可继续美化",
];
