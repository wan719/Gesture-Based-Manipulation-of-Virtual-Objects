export const techTags = [
  "MediaPipe",
  "Python",
  "FastAPI",
  "WebSocket",
  "Unity WebGL",
  "React Dashboard",
];

export const pipelineSteps = [
  "Camera",
  "Python MediaPipe Server",
  "WebSocket / MJPEG",
  "React Dashboard",
  "Unity WebGL",
  "RobotDog",
];

export const gestureMappings = [
  {
    gesture: "FIST",
    id: 0,
    action: "sit",
    description: "Robot dog crouches down.",
  },
  {
    gesture: "OPEN_PALM",
    id: 1,
    action: "idle",
    description: "Robot dog stays in idle mode.",
  },
  {
    gesture: "POINT_INDEX",
    id: 2,
    action: "forward",
    description: "Robot dog moves forward.",
  },
  {
    gesture: "VICTORY",
    id: 3,
    action: "backward",
    description: "Robot dog moves backward.",
  },
  {
    gesture: "THUMBS_UP",
    id: 4,
    action: "wave",
    description: "Robot dog performs a wave interaction.",
  },
];

export const actionButtons = [
  { label: "Idle", action: "idle" },
  { label: "Forward", action: "forward" },
  { label: "Backward", action: "backward" },
  { label: "Sit", action: "sit" },
  { label: "Wave", action: "wave" },
];

export const actionDescriptions = {
  idle: "Robot dog stays in idle mode.",
  forward: "Robot dog is moving forward.",
  backward: "Robot dog is stepping backward.",
  sit: "Robot dog crouches down.",
  wave: "Robot dog performs a wave interaction.",
  none: "Robot dog is waiting for a stable gesture command.",
};

export const completedItems = [
  "MediaPipe gesture recognition",
  "Stable gesture classification",
  "Python-to-Unity communication",
  "Unity robot dog control",
  "Web dashboard",
  "Python camera stream",
  "Unity WebGL integration design",
];

export const limitationItems = [
  "Unity WebGL build requires manual export from Unity Editor",
  "Robot dog animation is still basic code-driven animation",
  "Scene background can be further polished",
];
