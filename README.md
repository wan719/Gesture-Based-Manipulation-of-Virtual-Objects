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
