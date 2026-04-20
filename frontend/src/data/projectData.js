export const techTags = ["MediaPipe", "Python", "UDP", "Unity", "RobotDog"];

export const pipelineSteps = [
  "摄像头 Camera",
  "MediaPipe Hands",
  "手势分类器 Gesture Classifier",
  "UDP",
  "Unity",
  "虚拟机械狗 Virtual Robot Dog",
];

export const gestureMappings = [
  { gesture: "FIST", id: 0, action: "sit" },
  { gesture: "OPEN_PALM", id: 1, action: "idle" },
  { gesture: "POINT_INDEX", id: 2, action: "forward" },
  { gesture: "VICTORY", id: 3, action: "backward" },
  { gesture: "THUMBS_UP", id: 4, action: "wave" },
];

export const highlights = [
  {
    title: "实时手势识别",
    description:
      "通过 MediaPipe Hands 跟踪手部关键点，对摄像头输入进行实时、稳定的手势识别。",
  },
  {
    title: "低延迟 UDP 通信",
    description:
      "Python 端将紧凑 JSON 消息通过 UDP 发送到 Unity，快速触发机械狗动作。",
  },
  {
    title: "Unity 虚拟机械狗控制",
    description:
      "手势 ID 直接映射到动画状态，在交互场景中驱动虚拟机械狗执行动作。",
  },
  {
    title: "动作稳定与平滑优化",
    description:
      "通过稳定帧确认与动作平滑策略减少抖动，提升演示过程的自然性与可靠性。",
  },
];

export const actionButtons = [
  { label: "待机（idle）", action: "idle" },
  { label: "前进（forward）", action: "forward" },
  { label: "后退（backward）", action: "backward" },
  { label: "坐下（sit）", action: "sit" },
  { label: "挥手（wave）", action: "wave" },
];
