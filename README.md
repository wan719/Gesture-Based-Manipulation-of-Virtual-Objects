# Gesture-Based Manipulation of Virtual Objects

基于手势识别控制虚拟机械狗的课程项目。  
系统链路：`Camera -> MediaPipe Hands -> Gesture Classifier -> UDP -> Unity -> Virtual Robot Dog`

## 项目亮点

- 已支持 5 类手势识别：`FIST`、`OPEN_PALM`、`POINT_INDEX`、`VICTORY`、`THUMBS_UP`
- 手势映射动作：`sit` / `idle` / `forward` / `backward` / `wave`
- Python 通过 UDP 向 Unity 发送动作指令
- 增加稳定帧确认与动作平滑优化
- 增加前端桥接服务（FastAPI + WebSocket），实现网页实时状态看板

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

## 安装依赖

在项目根目录执行：

```bash
pip install opencv-python mediapipe numpy fastapi uvicorn requests
```

前端依赖：

```bash
cd frontend
npm install
```

## 一键理解：三进程启动顺序

你需要开 3 个终端窗口。

### 终端 1：启动前端

```bash
cd frontend
npm run dev
```

浏览器打开 `http://localhost:5173`

### 终端 2：启动桥接服务（给前端推实时状态）

```bash
python src/gesture/dashboard_bridge.py
```

桥接服务地址：`http://127.0.0.1:8000`

- HTTP 拉取：`GET /api/status`
- HTTP 更新：`POST /api/update`
- WebSocket：`ws://127.0.0.1:8000/ws/status`

### 终端 3：启动手势识别主程序（同时发 Unity + 发前端）

```bash
python src/gesture/gesture_recognizer.py
```

默认 Unity UDP 目标：`127.0.0.1:5052`

## 手势映射表

| Gesture | ID | Action |
| --- | --- | --- |
| `FIST` | `0` | `sit` |
| `OPEN_PALM` | `1` | `idle` |
| `POINT_INDEX` | `2` | `forward` |
| `VICTORY` | `3` | `backward` |
| `THUMBS_UP` | `4` | `wave` |
| `UNKNOWN` | `5` | `none` |

## 前端模式说明

- `Live Mode`：读取 Python Bridge 实时数据（WebSocket）
- `Demo Mode`：本地按钮模拟动作，适合离线演示 UI

## 常见问题

### 1. 前端显示 “等待 Python Bridge 服务”

- 确认 `dashboard_bridge.py` 正在运行
- 确认端口 `8000` 没被占用
- 确认浏览器可访问 `http://127.0.0.1:8000/api/status`

### 2. 手势识别能跑，但前端没更新

- 确认 `gesture_recognizer.py` 没有报 `requests` 模块错误
- 重新安装依赖：`pip install requests`

### 3. 摄像头打不开

- 关闭占用摄像头的软件（会议软件、聊天软件等）
- 检查系统权限是否允许 Python 使用摄像头

## 仅做 UDP 联调（可选）

如果你只想测试 UDP 通信：

```bash
python udp_receiver.py
python gesture_udp_sender.py
```

默认使用 `127.0.0.1:8888` 做收发测试。

