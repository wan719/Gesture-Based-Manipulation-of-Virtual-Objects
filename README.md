# Gesture-Based Manipulation of Virtual Objects

基于手势识别控制虚拟机械狗的课程项目。  
系统链路：`Camera -> MediaPipe Hands -> Gesture Classifier -> UDP -> Unity -> Virtual Robot Dog`

## 项目亮点

- 支持 5 类手势：`FIST`、`OPEN_PALM`、`POINT_INDEX`、`VICTORY`、`THUMBS_UP`
- 手势映射动作：`sit / idle / forward / backward / wave`
- Python 通过 UDP 向 Unity 发送动作指令
- 已加入稳定帧确认与动作平滑优化
- 前端通过 FastAPI + WebSocket 实时展示状态

## 目录结构

```text
.
├─ src/
│  └─ gesture/
│     ├─ feature_extractor.py
│     ├─ gesture_classifier.py
│     ├─ gesture_recognizer.py
│     ├─ udp_sender.py
│     └─ dashboard_bridge.py
├─ frontend/
├─ gesture_udp_sender.py
├─ udp_receiver.py
└─ README.md
```

## 环境要求

- Python 3.9+
- Node.js 18+
- 摄像头可用

## 重要说明（路径问题）

Windows 下 MediaPipe 在某些情况下会受到**中文路径**影响，导致资源加载失败。  
本项目推荐使用下面这个英文路径解释器入口运行 Python：

`D:\tools\gesture_env_link\python.exe`

请不要混用：

- `E:\miniconda\python.exe`
- `python`（不确定指向哪个环境）

## 安装依赖

如需安装/补齐依赖（使用推荐解释器）：

```bash
D:\tools\gesture_env_link\python.exe -m pip install opencv-python mediapipe==0.10.9 requests fastapi uvicorn websockets wsproto
```

前端依赖：

```bash
cd frontend
npm install
```

## 启动方式（三终端）

### 终端 1：前端

```bash
cd frontend
npm run dev
```

浏览器访问：`http://localhost:5173`

### 终端 2：桥接服务

```bash
D:\tools\gesture_env_link\python.exe src/gesture/dashboard_bridge.py
```

桥接服务地址：`http://127.0.0.1:8000`

- 状态接口：`GET /api/status`
- 更新接口：`POST /api/update`
- WebSocket：`ws://127.0.0.1:8000/ws/status`

### 终端 3：手势识别主程序

```bash
D:\tools\gesture_env_link\python.exe src/gesture/gesture_recognizer.py
```

默认 UDP 目标：`127.0.0.1:5052`

## 手势映射表

| Gesture | ID | Action |
| --- | --- | --- |
| `FIST` | `0` | `sit` |
| `OPEN_PALM` | `1` | `idle` |
| `POINT_INDEX` | `2` | `forward` |
| `VICTORY` | `3` | `backward` |
| `THUMBS_UP` | `4` | `wave` |
| `UNKNOWN` | `5` | `none` |

## 前端说明

- `Live Mode`：显示 Python 实时状态（WebSocket）
- `Demo Mode`：本地按钮演示模式
- 左侧导航栏在桌面端滚动时保持固定
- 页面只保留浏览器主滚动条（无内层双滚动条）

## 常见问题

### 1. 前端显示“等待 Python Bridge 服务”

- 确认 `dashboard_bridge.py` 正在运行
- 确认 `http://127.0.0.1:8000/api/status` 可访问

### 2. 手势识别程序启动后直接退出

- 确认使用的是 `D:\tools\gesture_env_link\python.exe`
- 不要用 `E:\miniconda\python.exe` 运行本项目主程序

### 3. 桥接日志很多 `GET /api/status`

- 这是前端兜底轮询，WebSocket稳定后会明显减少
- 不影响实时功能

### 4. `GET /favicon.ico 404`

- 正常现象，不影响系统功能

## 仅做 UDP 联调（可选）

```bash
D:\tools\gesture_env_link\python.exe udp_receiver.py
D:\tools\gesture_env_link\python.exe gesture_udp_sender.py
```

默认联调端口：`127.0.0.1:8888`

## 理想完整版展示系统

最终展示链路：

```text
Camera -> Python MediaPipe Server -> WebSocket/MJPEG -> React Dashboard -> Unity WebGL -> RobotDog
```

这一链路与桌面版 Unity UDP 联调并存：

- Desktop Unity 使用 UDP，Python 通过 `UDPSender` 向桌面 Unity 发送 `gesture_id`。
- WebGL Unity 不使用 UDP Socket，由 React 在网页中调用 `unityInstance.SendMessage("RobotDog", "SetAction", action)`。
- `UdpReceiver.cs` 等桌面 Unity 文件应继续保留，不需要删除。

### Python 识别服务

```bash
cd python_gesture
pip install -r requirements-dashboard.txt
python gesture_dashboard_server.py
```

默认服务地址：`http://127.0.0.1:8000`

接口：

- `GET /api/status`
- `GET /video_feed`
- `POST /api/update`
- `WebSocket /ws/status`

如果还要同时发送 UDP 给桌面 Unity：

```bash
python gesture_dashboard_server.py --enable-udp --udp-ip 127.0.0.1 --udp-port 5052
```

### 前端运行

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：`http://127.0.0.1:5173`

### Unity WebGL Build 放置路径

将 Unity WebGL 导出结果放入：

```text
frontend/public/unity-build/
```

推荐目录结构：

```text
frontend/public/unity-build/
├─ index.html
├─ Build/
└─ TemplateData/
```

前端默认加载：

```text
frontend/public/unity-build/Build/unity-build.loader.js
frontend/public/unity-build/Build/unity-build.data
frontend/public/unity-build/Build/unity-build.framework.js
frontend/public/unity-build/Build/unity-build.wasm
```

当前仓库已检测到的 Unity WebGL Build 文件：

```text
frontend/public/unity-build/
├─ index.html
├─ Build/
│  ├─ unity-build.loader.js
│  ├─ unity-build.data
│  ├─ unity-build.framework.js
│  └─ unity-build.wasm
└─ TemplateData/
```

当前导出文件未使用 `.br` 或 `.gz` 压缩后缀，Vite 本地服务可直接访问这些文件。

如果 Unity 导出的文件名不是 `unity-build.*`，请修改：

```text
frontend/src/hooks/useUnityWebGL.js
```

当前前端中 `UNITY_BUILD_CONFIG` 会把 Unity loader 加载到中间栏的 canvas。Unity 加载完成后，状态会显示 `Unity Ready`。Demo Mode 点击 `Idle / Forward / Backward / Sit / Wave` 时，React 会直接调用：

```javascript
unityInstance.SendMessage("RobotDog", "SetAction", action)
```

Live Mode 收到 Python WebSocket 推送后，也会用同一方式把 `action` 转发给 Unity WebGL。

### 常见问题

#### 摄像头打不开

- 确认摄像头没有被其他程序占用。
- 尝试 `python gesture_dashboard_server.py --camera-index 1`。
- 访问 `http://127.0.0.1:8000/video_feed`，如果摄像头不可用，会显示错误占位帧。

#### WebSocket 未连接

- 确认 Python 服务正在运行。
- 访问 `http://127.0.0.1:8000/api/status`，应返回 JSON。
- 前端 Live Mode 会显示 `Waiting for Python Bridge`，不会导致页面崩溃。

#### Unity WebGL Build Not Found

- 确认已经导出 Unity WebGL。
- 确认文件在 `frontend/public/unity-build/`。
- 确认 `Build/*.loader.js` 文件名与 `useUnityWebGL.js` 中的路径一致。
- 如果导出文件带 `.br` 或 `.gz` 后缀且浏览器加载失败，建议在 Unity 中设置 `Compression Format = Disabled` 后重新 Build。

#### Unity 对象名不是 RobotDog

修改：

```text
frontend/src/hooks/useUnityWebGL.js
```

将：

```javascript
export const UNITY_TARGET_OBJECT = "RobotDog";
```

改为场景中的实际对象名。

#### SendMessage 没反应

- 确认 Unity 场景对象挂载了 `DogController`。
- 确认 `DogController` 有 `public void SetAction(string action)`。
- 确认 action 字符串为 `idle / forward / backward / sit / wave`。
- 打开浏览器控制台检查 Unity WebGL 加载错误。

Unity WebGL 导出步骤见：[docs/unity-webgl-export-guide.md](docs/unity-webgl-export-guide.md)。
